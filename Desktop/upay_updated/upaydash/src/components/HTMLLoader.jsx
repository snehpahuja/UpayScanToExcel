import React, { useEffect, useRef, useState } from 'react'

export default function HTMLLoader({ page }) {
  const containerRef = useRef(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    const addedLinks = []
    const addedStyles = []

    async function load() {
      setError(null)
      try {
        const res = await fetch(page)
        if (!res.ok) throw new Error('Failed to load prototype HTML')
        const text = await res.text()

        if (cancelled) return

        // Create a DOM parser to extract head elements
        const parser = new DOMParser()
        const doc = parser.parseFromString(text, 'text/html')

        // Inject stylesheets (<link rel="stylesheet">) into document.head if not already present
        doc.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
          const href = link.getAttribute('href')
          if (!href) return
          // avoid duplicates
          if (![...document.head.querySelectorAll('link[rel=\"stylesheet\"]')].some(l => l.getAttribute('href') === href)) {
            const newLink = document.createElement('link')
            newLink.rel = 'stylesheet'
            newLink.href = href
            document.head.appendChild(newLink)
            addedLinks.push(newLink)
          }
        })

        // Inject inline <style> tags into head (avoid duplicates by comparing textContent)
        doc.querySelectorAll('style').forEach(style => {
          const textContent = style.textContent || ''
          if (![...document.head.querySelectorAll('style')].some(s => s.textContent === textContent)) {
            const newStyle = document.createElement('style')
            newStyle.textContent = textContent
            document.head.appendChild(newStyle)
            addedStyles.push(newStyle)
          }
        })

        // Remove head elements from the fragment (we only want body markup rendered)
        doc.querySelectorAll('head > *').forEach(n => n.remove())

        // Insert body HTML into container
        if (containerRef.current) {
          containerRef.current.innerHTML = ''
          // Move body children safely
          Array.from(doc.body.childNodes).forEach(node => {
            containerRef.current.appendChild(document.importNode(node, true))
          })
        }
      } catch (err) {
        console.error(err)
        setError(err.message || String(err))
      }
    }

    load()

    return () => {
      cancelled = true
      // cleanup injected stylesheets and style tags
      addedLinks.forEach(l => l.remove())
      addedStyles.forEach(s => s.remove())
      if (containerRef.current) containerRef.current.innerHTML = ''
    }
  }, [page])

  return (
    <div>
      {error ? (
        <div className="p-4 bg-red-50 text-red-700 rounded">Error loading prototype: {error}</div>
      ) : (
        <div ref={containerRef} />
      )}
    </div>
  )
}
