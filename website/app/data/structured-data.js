import { siteContent } from './site-content.js'

const siteUrl = 'https://www.shcoolhelper.cn'

export const structuredData = [
  {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: siteContent.brand,
    description: siteContent.seo.description,
    url: siteUrl,
    applicationCategory: 'UtilitiesApplication',
    operatingSystem: 'Windows',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'CNY'
    },
    featureList: siteContent.features,
    softwareVersion: siteContent.download.version,
    datePublished: siteContent.download.updatedAt,
    downloadUrl: `${siteUrl}${siteContent.download.href}`,
    publisher: {
      '@type': 'Organization',
      name: siteContent.brand
    }
  },
  {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: siteContent.faq.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer
      }
    }))
  }
]
