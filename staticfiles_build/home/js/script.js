const API_URL = 'https://quranapi.pages.dev/api/surah.json';

const surahList = document.getElementById('surahList');
const sidebar = document.getElementById('left-sidebar');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const closeBtn = document.getElementById('close');
const searchInputs = document.querySelectorAll('input');

// Toggle sidebar visibility with animation
function toggleSidebar() {
    sidebar.classList.toggle('active');
    sidebarOverlay.classList.toggle('active');
    closeBtn.classList.toggle('active');
    document.body.classList.toggle('sidebar-open');
}

// Close sidebar
function closeSidebar() {
    sidebar.classList.remove('active');
    sidebarOverlay.classList.remove('active');
    closeBtn.classList.remove('active');
    document.body.classList.remove('sidebar-open');
}

// Event listeners for sidebar
closeBtn.addEventListener('click', toggleSidebar);
sidebarOverlay.addEventListener('click', closeSidebar);

// Close sidebar on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar.classList.contains('active')) {
        closeSidebar();
    }
});

// Fetch and display surahs from API
async function fetchSurahs() {
    try {
        const response = await fetch(API_URL);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displaySurahs(data);
        
    } catch (error) {
        console.error('Error fetching surahs:', error);
        displayError();
    }
}

// Display error message
function displayError() {
    surahList.innerHTML = `
        <div style="color: #f9f7e8; padding: 2rem; text-align: center; grid-column: 1/-1;">
            <p>Failed to load surahs. Please check your internet connection and try again.</p>
        </div>
    `;
}

// Display surahs in the grid
function displaySurahs(surahs) {
    surahList.innerHTML = '';
    
    surahs.forEach((surah, index) => {
        const surahBox = createSurahBox(surah, index + 1);
        surahList.appendChild(surahBox);
    });
}

// Create individual surah box element
function createSurahBox(surah, number) {
    const surahBox = document.createElement('div');
    surahBox.className = 'surah-box';
    surahBox.setAttribute('data-surah-number', surah.surahNumber);
    
    surahBox.innerHTML = `
        <div class="list">
            <p>${number}</p>
        </div>
        <div class="surah-name">
            <p class="arabic-name">${surah.surahName}</p>
            <p class="english-name">${surah.surahNameTranslation}</p>
        </div>
        <div>
            <p class="arabic">${surah.surahNameArabic}</p>
            <p class="ayah">${surah.totalAyah} Ayahs</p>
        </div>
    `;
    
    return surahBox;
}

// Setup search functionality
function setupSearch() {
    searchInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            filterSurahs(searchTerm);
        });
    });
}

// Filter surahs based on search term
function filterSurahs(searchTerm) {
    const surahBoxes = document.querySelectorAll('.surah-box');
    
    surahBoxes.forEach(box => {
        const arabicName = box.querySelector('.arabic-name').textContent.toLowerCase();
        const englishName = box.querySelector('.english-name').textContent.toLowerCase();
        const ayahText = box.querySelector('.ayah').textContent.toLowerCase();
        
        const isMatch = arabicName.includes(searchTerm) || 
                       englishName.includes(searchTerm) || 
                       ayahText.includes(searchTerm);
        
        box.style.display = isMatch ? 'flex' : 'none';
    });
}

// Initialize
fetchSurahs();
setupSearch();