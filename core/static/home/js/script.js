const API_URL = 'https://quranapi.pages.dev/api/surah.json';

const surahList = document.getElementById('surahList');
const sidebar = document.getElementById('left-sidebar');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const closeBtn = document.getElementById('close');
const searchInput = document.querySelector('.search-bar input');


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
            <button onclick="location.reload()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--tigers-eye); color: var(--cornsilk); border: none; border-radius: 0.5rem; cursor: pointer;">Refresh</button>
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
    surahBox.setAttribute('data-surah-number', number);

    
    surahBox.innerHTML = `
        <div class="list">
            <p>${number}</p>
        </div>
        <div class="surah-name">
            <p class="arabic-name">${surah.surahName}</p>
            <p class="english-name">${surah.surahNameTranslation}</p>
        </div>
        <div class="surah-info">
            <p class="arabic">${surah.surahNameArabic}</p>
            <p class="ayah">${surah.totalAyah} Ayahs</p>
        </div>
    `;
    
    // Click surah to go to audio page
    surahBox.addEventListener('click', (e) => {
        window.location.href = `/surah/audio/${number}/`;
    });
    
    return surahBox;
}

// Show notification toast
function showNotification(message, type = 'info') {
    const existing = document.querySelector('.notification-toast');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = `notification-toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Setup search functionality
function setupSearch() {
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const searchTerm = e.target.value.toLowerCase().trim();
            filterSurahs(searchTerm);
        }, 300);
    });
}

// Filter surahs based on search term
function filterSurahs(searchTerm) {
    const surahBoxes = document.querySelectorAll('.surah-box');
    let visibleCount = 0;
    
    surahBoxes.forEach(box => {
        const arabicName = box.querySelector('.arabic-name').textContent.toLowerCase();
        const englishName = box.querySelector('.english-name').textContent.toLowerCase();
        const arabicScript = box.querySelector('.arabic').textContent;
        const surahNumber = box.querySelector('.list p').textContent;
        const ayahText = box.querySelector('.ayah').textContent.toLowerCase();
        
        const isMatch = searchTerm === '' ||
                       arabicName.includes(searchTerm) || 
                       englishName.includes(searchTerm) || 
                       arabicScript.includes(searchTerm) ||
                       surahNumber === searchTerm ||
                       ayahText.includes(searchTerm);
        
        if (isMatch) {
            box.style.display = 'flex';
            box.style.animation = 'fadeIn 0.3s ease';
            visibleCount++;
        } else {
            box.style.display = 'none';
        }
    });
    
    showNoResultsMessage(visibleCount, searchTerm);
}

// Show no results message
function showNoResultsMessage(count, searchTerm) {
    let noResultsDiv = document.querySelector('.no-results');
    
    if (count === 0 && searchTerm !== '') {
        if (!noResultsDiv) {
            noResultsDiv = document.createElement('div');
            noResultsDiv.className = 'no-results';
            noResultsDiv.style.cssText = `
                grid-column: 1/-1;
                text-align: center;
                padding: 3rem 2rem;
                color: var(--cornsilk);
            `;
            surahList.appendChild(noResultsDiv);
        }
        noResultsDiv.innerHTML = `
            <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">No surahs found</p>
            <p style="opacity: 0.8;">Try searching with different keywords</p>
        `;
    } else if (noResultsDiv) {
        noResultsDiv.remove();
    }
}

// Initialize
fetchSurahs();
setupSearch();