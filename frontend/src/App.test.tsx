import { describe, expect, it } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'
import App from './App'

describe('App', () => {
  it('renders the application title', () => {
    const html = renderToStaticMarkup(<App />)
    expect(html).toContain('Urban Traffic Management')
  })
})
