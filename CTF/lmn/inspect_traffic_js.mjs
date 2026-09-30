const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

async function main() {
  const res = await fetch('https://layma.net/Traffic/Index/x5iqMXEcU', {
    headers: { 'User-Agent': UA }
  });
  const text = await res.text();
  console.log('Total length:', text.length);

  // Search for API endpoints
  const endpoints = text.match(/https?:\/\/[^\s"'`]+|api\/[^\s"'`]+/g) || [];
  console.log('Endpoints found:', [...new Set(endpoints)]);

  // Search for campain query parameters
  const campIndex = text.indexOf('campain');
  if (campIndex !== -1) {
    console.log('Context around campain:', text.slice(Math.max(0, campIndex - 200), campIndex + 300));
  } else {
    console.log('No campain found in script directly');
  }

  // Let's also check flatform
  const lines = text.split('\n');
  for (let l of lines) {
    if (l.includes('flatform') || l.includes('campain') || l.includes('tructiep') || l.includes('google')) {
      console.log('Line match:', l.trim().slice(0, 200));
    }
  }
}

main().catch(console.error);
