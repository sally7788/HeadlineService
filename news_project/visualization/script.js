function fetchNews(keyword) {
  const titleEl = document.getElementById('results-title');
  const listEl  = document.getElementById('news-list-container');
  const panelEl = document.querySelector('.right-panel');

  if (!listEl) return;
  titleEl.hidden = false;
  listEl.hidden  = false;
  if (panelEl) panelEl.hidden = false;

  listEl.innerHTML = '';
  const news = window.mockNewsData[keyword] || [];
  if (news.length) {
    news.forEach(n => {
      const li = document.createElement('li');
      li.innerHTML = `<a href="${n.url}" target="_blank">${n.title}</a>`;
      listEl.appendChild(li);
    });
  } else {
    listEl.innerHTML = '<li>관련 뉴스 없음</li>';
  }
}

// 워드 클라우드 생성용 임시 데이터
function drawWordCloud() {
  const words = [
    ["superman", 27],
    ["batman", 8],
    ["wonder woman", 2],
    ["kryptonite", 9],
        ["lex luthor", 5],
    ["dc comics", 4],
    ["krypton", 3],
    ["smallville", 3],
    ["cape", 2],
    ["daily planet", 2],
    ["superboy", 1],
    ["jor-el", 1],
    ["metropolis", 3],
    ["clark kent", 5],
    ["christopher reeve", 1],
    ["united states", 1],
    ["action comics", 1],
    ["demigod", 1],
    ["clark", 3],
    ["superheroes", 3],
    ["aquaman", 1],
    ["movie", 1],
    ["villain", 1],
    ["cartoon", 1],
    ["high school", 1],
    ["supervillain", 1],
    ["kent", 2],
    ["spider man", 1],
    ["comic books", 1],
    ["marvel comic", 1],
    ["silver surfer", 1],
    ["american comic book", 1],
    ["flash", 1],
    ["lois", 3],
    ["super hero", 1],
    ["justice league", 2],
    ["captain", 1],
    ["monster", 1],
    ["action", 1],
    ["justice league of america", 2],
    ["justice", 1],
    ["invisible man", 1],
    ["spider-man", 1],
    ["zod", 2],
    ["doomsday", 2],
    ["spiderman", 1],
    ["homelander", 1],
    ["lex", 2]
  ];

  const wordCloudElement = document.getElementById('word-cloud-html');

  WordCloud(wordCloudElement, {
    list: words,
    classes: 'word-cloud-item',
    gridSize: 10,
    color: 'random-dark',
    rotateRatio: 0,
    weightFactor: 10,
    shrinkToFit: true
  });


  // 렌더 완료 이벤트 후 span에 클릭 연결
  wordCloudElement.addEventListener('wordcloudstop', () => {
    
    const spans = Array.from(document.querySelectorAll('#word-cloud-html .word-cloud-item'));
    wordCloudElement.classList.remove('entered');
    spans.forEach((span, idx) => {
      span.style.transition = 'opacity 420ms ease, transform 420ms ease';
      span.style.transitionDelay = `${Math.min(idx * 12, 240)}ms`;
      // 애니메이션 지연 설정
      span.style.setProperty('--i', idx);
    });
    requestAnimationFrame(() => {
      wordCloudElement.classList.add('entered');
    });

    document.querySelectorAll('#word-cloud-html .word-cloud-item')
      .forEach(span => {
        span.addEventListener('click', () => {
          const keyword = span.textContent;
          fetchNews(keyword);
        });
      });

    const rect = wordCloudElement.getBoundingClientRect();
    let raf;
    function onMove(e){
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const cx = rect.width / 2;
      const cy = rect.height / 2;
      const nx = (x - cx) / cx; // -1..1
      const ny = (y - cy) / cy; // -1..1
      if (raf) cancelAnimationFrame(raf);
      raf = requestAnimationFrame(()=>{
        spans.forEach((s,i)=>{
          const strength = 3; // px
          s.style.setProperty('--mx', `${nx * strength}px`);
          s.style.setProperty('--my', `${ny * strength}px`);
        });
      });
    }
    wordCloudElement.addEventListener('mousemove', onMove);
  });
}


let currentFilters = {
  press: null,
  dateRange: null,
  searchTerm: null
};

// 검색
document.addEventListener('DOMContentLoaded', () => {
  drawWordCloud();
  
  const searchForm = document.getElementById('search-form');
  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const searchInput = document.getElementById('search-input');
      const searchTerm = searchInput.value.trim();
      
      if (searchTerm) {
        // 검색 시 카테고리 필터 초기화 (카테고리에 맞추어 검색되는 것을 방지)
        currentFilters.searchTerm = searchTerm;
        currentFilters.press = null;
        currentFilters.dateRange = null;
        filterWordCloud();
        searchInput.value = '';
        
        // 카테고리 선택 상태 초기화
        document.querySelectorAll('.collapse-item').forEach(item => {
          item.classList.remove('active');
        });
      }
    });
  }

  // 카테고리 필터
  setupCategoryFilters();
});


function setupCategoryFilters() {
  // 언론사별
  const pressItems = document.querySelectorAll('#collapsePress .collapse-item');
  pressItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const pressName = item.textContent.trim();
      currentFilters.press = pressName;
      currentFilters.dateRange = null; // 초기화
      filterWordCloud();
      updateActiveFilter('press', pressName);
    });
  });

  // 날짜별
  const dateItems = document.querySelectorAll('#collapseWeather .collapse-item');
  dateItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const dateRange = item.textContent.trim();
      currentFilters.dateRange = dateRange;
      currentFilters.press = null; // 초기화
      filterWordCloud();
      updateActiveFilter('date', dateRange);
    });
  });
}

// 필터 시각화
function updateActiveFilter(type, value) {
  
  document.querySelectorAll('.collapse-item').forEach(item => {
    item.classList.remove('active');
  });
  
  const items = document.querySelectorAll('.collapse-item');
  items.forEach(item => {
    if (item.textContent.trim() === value) {
      item.classList.add('active');
    }
  });
}

// 필터링 
function filterWordCloud() {
  const wordCloudElement = document.getElementById('word-cloud-html');
  if (!wordCloudElement) return;

  // 필터 설명
  let filterDesc = '';
  if (currentFilters.press) {
    filterDesc = `${currentFilters.press} 언론사`;
  } else if (currentFilters.dateRange) {
    filterDesc = `${currentFilters.dateRange} 뉴스`;
  } else if (currentFilters.searchTerm) {
    filterDesc = `"${currentFilters.searchTerm}" 검색 결과`;
  } else {
    filterDesc = '전체 뉴스';
  }

  // 로딩 메세지
  wordCloudElement.innerHTML = `<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666; flex-direction: column;">
    <div class="spinner-border text-primary mb-3" role="status">
      <span class="sr-only">로딩중...</span>
    </div>
    <p>${filterDesc}를 불러오는 중...</p>
  </div>`;
  
  // API 호출 시 워드 클라우드 다시 그리기
  setTimeout(() => {
    // 이 부분에서 API 호출
    console.log('Current filters:', currentFilters);
    drawWordCloud();
  }, 1000);
}

let resizeTimer; 


window.addEventListener('resize', function() {

    clearTimeout(resizeTimer);
    
    resizeTimer = setTimeout(function() {
        drawWordCloud();
    }, 200);
});