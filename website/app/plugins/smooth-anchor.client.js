export default defineNuxtPlugin(() => {
  const scrollToHashTarget = (event) => {
    if (event.defaultPrevented) return

    const anchor = event.target.closest('a[href^="#"]')

    if (!anchor) {
      return
    }

    const target = document.querySelector(anchor.getAttribute('href'))

    if (!target) {
      return
    }

    event.preventDefault()
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  document.addEventListener('click', scrollToHashTarget)
})
