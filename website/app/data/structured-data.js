import { siteContent } from './site-content.js'

const siteUrl = 'https://www.schoolhelper.cn'

export function buildStructuredData(content) {
  return [
    {
      '@context': 'https://schema.org',
      '@type': 'SoftwareApplication',
      name: content.brand,
      description: content.seo.description,
      url: siteUrl,
      applicationCategory: 'UtilitiesApplication',
      operatingSystem: 'Windows',
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'CNY'
      },
      featureList: content.features,
      softwareVersion: content.download.version,
      datePublished: content.download.updatedAt,
      downloadUrl: `${siteUrl}${content.download.href}`,
      publisher: {
        '@type': 'Organization',
        name: content.brand
      }
    },
    {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: content.faq.map((item) => ({
        '@type': 'Question',
        name: item.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: item.answer
        }
      }))
    }
  ]
}

export const structuredData = buildStructuredData(siteContent)
