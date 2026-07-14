<template>
  <header class="top">
    <div class="top-inner">
      <router-link class="brand" to="/">
        <div class="brand-mark">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M3 15c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2" stroke="#E8B23D" stroke-width="2" stroke-linecap="round" /><path d="M3 20c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity="0.6" /></svg>
        </div>
        <span class="brand-name">LocalHub</span>
        <span class="brand-region">부산</span>
      </router-link>
      <nav class="main">
        <router-link to="/" class="nav-btn">홈</router-link>
        <router-link to="/board" class="nav-btn">게시판</router-link>
        <router-link to="/map" class="nav-btn">지도</router-link>
      </nav>
    </div>
  </header>
</template>
