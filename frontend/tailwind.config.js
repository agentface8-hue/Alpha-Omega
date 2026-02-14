/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // "War Room" Theme
                neon: {
                    green: '#00ff41',
                    blue: '#00ccff',
                    red: '#ff003c',
                },
                dark: {
                    bg: '#0a0a0a',
                    card: '#111111',
                    border: '#222222',
                }
            },
            fontFamily: {
                mono: ['Fira Code', 'monospace', 'ui-monospace', 'SFMono-Regular']
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
        },
    },
    plugins: [],
}
