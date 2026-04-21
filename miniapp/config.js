const ENV = 'dev'

const CONFIGS = {
  dev: {
    apiBaseUrl: 'http://127.0.0.1:8000/api'
  },
  prod: {
    apiBaseUrl: 'https://your-domain.com/api'
  }
}

const config = CONFIGS[ENV]

module.exports = config
