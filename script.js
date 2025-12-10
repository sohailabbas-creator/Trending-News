* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #f4f4f4; line-height: 1.6; }
header { background: #111; color: #fff; padding: 20px; text-align: center; }
h1 { margin: 0; font-size: 2rem; }

.news-container { max-width: 1200px; margin: 20px auto; padding: 10px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; }
.card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between; }
.card h2 { font-size: 1.2rem; margin-bottom: 10px; }
.card p { flex-grow: 1; }
.card a { text-decoration: none; color: #0077cc; margin-top: 10px; display: inline-block; }
.card a:hover { text-decoration: underline; }

.loader { text-align: center; font-size: 18px; padding: 20px; }
footer { background:#111; color:#fff; text-align:center; padding:20px; margin-top:20px; }
footer a { color:#fff; margin:0 10px; text-decoration:none; }
footer a:hover { text-decoration:underline; }

@media (max-width: 768px) {
  header h1 { font-size: 1.5rem; }
  .card h2 { font-size: 1rem; }
}
@media (max-width: 480px) {
  .news-container { padding: 5px; grid-template-columns: 1fr; }
  .card { padding: 15px; }
  .card h2 { font-size: 0.95rem; }
}
