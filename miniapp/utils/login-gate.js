function createLoginGateModel(pageTitle) {
  const pageConfig = {
    '设备列表': {
      icon: '屏',
      highlights: ['同步你的设备归属关系', '查看在线状态和版本', '快速进入绑定流程']
    },
    '发送通知': {
      icon: '发',
      highlights: ['恢复你的发送身份', '只展示属于你的在线设备', '提交通知并追踪回执']
    },
    '发送记录': {
      icon: '记',
      highlights: ['读取你的历史通知记录', '查看设备展示回执', '按账号隔离通知数据']
    },
    '设备绑定': {
      icon: '绑',
      highlights: ['把设备绑定到当前微信身份', '防止误绑到其他账号', '扫码或输入绑定码继续']
    }
  }

  const current = pageConfig[pageTitle] || {
    icon: '我',
    highlights: ['恢复你的账号身份', '继续管理头像和昵称', '同步设备和通知数据']
  }

  return {
    eyebrow: '微信身份校验',
    sceneLabel: pageTitle,
    icon: current.icon,
    title: `登录后查看${pageTitle}`,
    description: `完成微信授权登录后，即可继续访问${pageTitle}，并恢复你当前账号下的设备、通知与记录。`,
    note: `无法查看当前${pageTitle}页面，请登录`,
    highlights: current.highlights
  }
}

module.exports = {
  createLoginGateModel
}
