/**
 * EquipmentShare.com Data Extractor
 * Run this script in the browser console to extract all equipment data
 */

// Category configuration
const CATEGORIES = [
  {
    name: "Aerial Work Platforms",
    url: "https://www.equipmentshare.com/rent/categories/aerial-work-platform",
    outputFile: "equipmentshare_aerial.json",
    keywords: ['lift', 'boom', 'scissor', 'atrium', 'mast'],
    exclude: ['forklift', 'telehandler', 'excavator', 'skid', 'dozer', 'crane', 'carrier', 'aerator', 'chipper', 'compressor', 'trencher', 'grinder', 'utility-vehicle']
  },
  {
    name: "Earthmoving",
    url: "https://www.equipmentshare.com/rent/categories/earthmoving",
    outputFile: "equipmentshare_earthmoving.json"
  },
  {
    name: "Forklifts & Material Handling",
    url: "https://www.equipmentshare.com/rent/categories/forklift-material-handling",
    outputFile: "equipmentshare_material_handling.json"
  }
];

// Extract data from a single equipment detail page
async function extractEquipmentData(url, categoryName) {
  console.log(`Extracting: ${url}`);

  // Navigate to the URL
  window.location.href = url;

  // Wait for page to load
  await new Promise(resolve => setTimeout(resolve, 3000));

  const data = {
    url: window.location.href,
    category: categoryName
  };

  // Get equipment name from h1
  const nameEl = document.querySelector('h1');
  if (nameEl) {
    data.name = nameEl.textContent.trim();
  }

  // Get equipment type from breadcrumb
  const breadcrumbLinks = document.querySelectorAll('[aria-label="Breadcrumb"] a, nav a');
  let equipmentType = "";
  breadcrumbLinks.forEach(link => {
    const text = link.textContent.trim();
    if (text.includes('Scissor') || text.includes('Boom') || text.includes('Lift') ||
        text.includes('Excavator') || text.includes('Forklift') || text.includes('Telehandler')) {
      equipmentType = text;
    }
  });
  data.equipment_type = equipmentType || categoryName;

  // Get pricing
  const priceText = document.body.textContent;
  const dayMatch = priceText.match(/\$(\d+,?\d*)\s*\/\s*day/);
  const weekMatch = priceText.match(/\$(\d+,?\d*)\s*\/\s*week/);
  const monthMatch = priceText.match(/\$(\d+,?\d*)\s*\/\s*4-week/);

  data.price_daily = dayMatch ? parseInt(dayMatch[1].replace(',', '')) : null;
  data.price_weekly = weekMatch ? parseInt(weekMatch[1].replace(',', '')) : null;
  data.price_monthly = monthMatch ? parseInt(monthMatch[1].replace(',', '')) : null;

  // Get brand/model from table
  const table = document.querySelector('table');
  let brands = [];
  let models = [];
  let specs = {};

  if (table) {
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
      const cells = row.querySelectorAll('td, th');
      if (cells.length >= 2) {
        const label = cells[0].textContent.trim();

        if (label === 'Equipment Make') {
          for (let i = 1; i < cells.length; i++) {
            const brand = cells[i].textContent.trim();
            if (brand && !brands.includes(brand)) {
              brands.push(brand);
            }
          }
        } else if (label === 'Model Number') {
          for (let i = 1; i < cells.length; i++) {
            const model = cells[i].textContent.trim();
            if (model && !models.includes(model)) {
              models.push(model);
            }
          }
        } else if (label === 'Capacity' || label === 'Max Working Height' || label === 'Operating Weight' ||
                   label === 'Dig Depth' || label === 'Reach Height' || label === 'Lift Capacity') {
          specs[label] = cells[1].textContent.trim();
        }
      }
    });
  }

  data.brand_model = brands.join(', ') + (models.length ? ' (' + models.join(', ') + ')' : '');
  data.specs = Object.entries(specs).map(([k, v]) => `${k}: ${v}`).join(', ');

  return data;
}

// Get all equipment URLs from a category page
async function getEquipmentUrls(categoryUrl, keywords = null, exclude = null) {
  console.log(`Loading category: ${categoryUrl}`);

  // Navigate to category page
  window.location.href = categoryUrl;
  await new Promise(resolve => setTimeout(resolve, 3000));

  // Scroll to bottom to load all items
  window.scrollTo(0, document.body.scrollHeight);
  await new Promise(resolve => setTimeout(resolve, 2000));
  window.scrollTo(0, document.body.scrollHeight);
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Collect all equipment URLs
  const links = document.querySelectorAll('a[href*="/rent/equipment-classes/"]');
  let urls = [];
  const seen = new Set();

  links.forEach(link => {
    const href = link.href;
    if (!seen.has(href)) {
      seen.add(href);
      urls.push(href);
    }
  });

  // Filter URLs if keywords provided
  if (keywords) {
    urls = urls.filter(u => keywords.some(kw => u.toLowerCase().includes(kw)));
  }

  // Exclude URLs if exclude list provided
  if (exclude) {
    urls = urls.filter(u => !exclude.some(kw => u.toLowerCase().includes(kw)));
  }

  console.log(`Found ${urls.length} equipment URLs`);
  return urls;
}

// Main extraction function
async function extractCategory(category) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`Extracting: ${category.name}`);
  console.log('='.repeat(60));

  // Get all equipment URLs
  const urls = await getEquipmentUrls(category.url, category.keywords, category.exclude);

  const allData = [];

  // Extract data from each equipment page
  for (let i = 0; i < urls.length; i++) {
    console.log(`[${i + 1}/${urls.length}]`);
    const data = await extractEquipmentData(urls[i], category.name);
    allData.push(data);
    await new Promise(resolve => setTimeout(resolve, 1500)); // Be polite
  }

  // Save to localStorage (since we can't write files directly from browser)
  localStorage.setItem(category.outputFile, JSON.stringify(allData, null, 2));

  console.log(`\nExtracted ${allData.length} items for ${category.name}`);
  console.log(`Data saved to localStorage['${category.outputFile}']`);
  console.log(`Copy the data using: copy(JSON.parse(localStorage.getItem('${category.outputFile}')))`);

  return allData;
}

// Run extraction for all categories
async function extractAll() {
  for (const category of CATEGORIES) {
    await extractCategory(category);
  }

  console.log('\n='.repeat(60));
  console.log('ALL EXTRACTIONS COMPLETE!');
  console.log('='.repeat(60));
  console.log('\nTo save the data, run these commands:');
  CATEGORIES.forEach(cat => {
    console.log(`copy(localStorage.getItem('${cat.outputFile}'))`);
  });
}

// Export functions for manual use
window.equipmentShareExtractor = {
  extractAll,
  extractCategory,
  getEquipmentUrls,
  extractEquipmentData,
  CATEGORIES
};

console.log('EquipmentShare Extractor loaded!');
console.log('Run: equipmentShareExtractor.extractAll() to start');
console.log('Or run individual category: equipmentShareExtractor.extractCategory(equipmentShareExtractor.CATEGORIES[0])');
