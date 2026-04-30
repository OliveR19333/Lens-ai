const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));

app.get('/health', (req, res) => res.send('OK'));

app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ LENS AI running on 0.0.0.0:${PORT}`);
});
