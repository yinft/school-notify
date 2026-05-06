import AOS from 'aos'

export default defineNuxtPlugin((nuxtApp) => {
  if ('scrollRestoration' in window.history) {
    window.history.scrollRestoration = 'manual'
  }

  const initAos = () => {
    if (window.location.hash) {
      window.history.replaceState(null, '', window.location.pathname + window.location.search)
    }

    AOS.init({
      anchorPlacement: 'top-bottom',
      duration: 1150,
      easing: 'ease-out-quart',
      once: true,
      offset: 72
    })

    if (!window.location.hash) {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
    }
  }

  onNuxtReady(() => {
    requestAnimationFrame(initAos)
  })

  nuxtApp.hook('page:finish', () => {
    requestAnimationFrame(() => {
      AOS.refreshHard()
    })
  })
})
