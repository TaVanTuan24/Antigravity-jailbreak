
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

async function main() {
  const targetDomain = 'madandesigns.in';
  console.log(`Fetching https://${targetDomain}/ ...`);
  const res = await fetch(`https://${targetDomain}/`, {
    headers: { 'User-Agent': UA }
  });
  console.log('Status:', res.status);
  const html = await res.text();
  console.log('HTML length:', html.length);

  // Check for any scripts or iframes or layma references
  const lines = html.split('\n');
  for (let line of lines) {
    if (line.toLowerCase().includes('layma') || line.toLowerCase().includes('traffic') || line.toLowerCase().includes('keytoken')) {
      console.log('MATCH:', line.trim());
    }
  }

  // Also check for any external scripts
  const scriptRegex = /<script[^>]+src=["']([^"']+)["']/gi;
  let match;
  while ((match = scriptRegex.exec(html)) !== null) {
    if (match[1].includes('layma') || match[1].includes('traffic') || match[1].includes('token') || match[1].includes('widget')) {
      console.log('SCRIPT SRC:', match[1]);
    }
  }
}

main().catch(console.error);
