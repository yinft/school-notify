from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps.auth import ensure_same_user, require_current_user
from app.schemas.notification import NotificationCreateRequest, NotificationCreateResponse, NotificationRecordListResponse
from app.services.device_connections import device_connections
from app.services.store import DeviceNotBoundError, DeviceNotFoundError, DeviceOfflineError, store


router = APIRouter(prefix="/notifications")


@router.get(
    "",
    summary="查询通知记录列表",
    description="【小程序端】分页查询指定用户发送的通知记录，包含每条通知在各设备上的投递状态。只能查询自己的通知。",
    responses={401: {"description": "未认证"}, 403: {"description": "无权查看其他用户的通知"}},
)
def list_notifications(
    sender_user_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user_id: str = Depends(require_current_user),
) -> NotificationRecordListResponse:
    ensure_same_user(expected_user_id=sender_user_id, current_user_id=current_user_id)
    items, total = store.list_notifications_for_user(sender_user_id=sender_user_id, limit=limit, offset=offset)
    return NotificationRecordListResponse(items=items, total=total)


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="发送通知",
    description="【小程序端】向指定设备列表发送通知。服务端创建通知记录后，通过 WebSocket 实时推送到在线设备。若目标设备离线则返回 409。",
    responses={
        202: {"description": "通知已接受，正在投递"},
        401: {"description": "未认证"},
        403: {"description": "设备未绑定到当前用户"},
        404: {"description": "设备不存在"},
        409: {"description": "设备离线"},
    },
)
async def create_notification(payload: NotificationCreateRequest, current_user_id: str = Depends(require_current_user)) -> NotificationCreateResponse:
    ensure_same_user(expected_user_id=payload.sender_user_id, current_user_id=current_user_id)
    try:
        response, deliveries = store.create_notification(
            sender_user_id=payload.sender_user_id,
            title=payload.title,
            content=payload.content,
            level=payload.level,
            device_ids=payload.device_ids,
            duration_seconds=payload.duration_seconds,
            tts_enabled=payload.tts_enabled,
            tts_repeat_count=payload.tts_repeat_count,
        )
        failed_device_ids = await device_connections.send_notifications(deliveries=deliveries)
        for failed_device_id in failed_device_ids:
            delivery = next(item for item in deliveries if item["device_id"] == failed_device_id)
            notification_id = str(delivery["payload"]["notification_id"])
            store.mark_delivery_failed(
                device_id=failed_device_id,
                notification_id=notification_id,
                error_message="device websocket not connected",
            )
        return response
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc
    except DeviceNotBoundError as exc:
        raise HTTPException(status_code=403, detail="device not bound to user") from exc
    except DeviceOfflineError as exc:
        raise HTTPException(status_code=409, detail="device offline") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
