<template>
  <div class="home-container">
    <div class="hero-section">
      <h1>Mafia Online</h1>
      <p class="subtitle">Грайте в класичну гру Мафія онлайн з друзями та незнайомцями</p>
      <div class="hero-buttons">
        <router-link to="/rooms" class="button primary">Почати гру</router-link>
        <router-link to="/leaderboard" class="button secondary">Таблиця лідерів</router-link>
      </div>
    </div>

    <div class="features-section">
      <h2>Особливості гри</h2>
      <div class="features-grid">
        <div class="feature-card card">
          <div class="feature-icon">👥</div>
          <h3>Мультиплеєр</h3>
          <p>Грайте з друзями та гравцями з усього світу</p>
        </div>

        <div class="feature-card card">
          <div class="feature-icon">🎭</div>
          <h3>Різні ролі</h3>
          <p>Мафія, мирні жителі та спеціальні ролі</p>
        </div>

        <div class="feature-card card">
          <div class="feature-icon">💬</div>
          <h3>Чат</h3>
          <p>Спілкуйтесь з іншими гравцями під час гри</p>
        </div>

        <div class="feature-card card">
          <div class="feature-icon">🏆</div>
          <h3>Рейтинг</h3>
          <p>Змагайтесь за місце в таблиці лідерів</p>
        </div>
      </div>
    </div>

    <div class="how-to-play-section card">
      <h2>Як грати</h2>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>Створіть акаунт</h3>
            <p>Зареєструйтесь або увійдіть у свій акаунт</p>
          </div>
        </div>

        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>Приєднуйтесь до кімнати</h3>
            <p>Виберіть існуючу кімнату або створіть нову</p>
          </div>
        </div>

        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>Отримайте роль</h3>
            <p>Чекайте початку гри та отримайте свою роль</p>
          </div>
        </div>

        <div class="step">
          <div class="step-number">4</div>
          <div class="step-content">
            <h3>Грайте</h3>
            <p>Використовуйте свої здібності та розкрийте мафію</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  margin: 0;
  /* Прибираємо жорсткий padding, бо тепер за це відповідає App.vue */
  padding: 1rem 0; 
}

.hero-section {
  text-align: center;
  padding: 3rem 1rem;
}

.hero-section h1 {
  font-size: 4rem; /* Зменшили з 4.5rem для кращого балансу */
  margin-bottom: 1rem;
  color: var(--accent-primary);
}

.subtitle {
  font-size: 1.6rem; /* Зменшили з 2rem */
  color: var(--text-secondary);
  margin-bottom: 2.5rem;
}

.hero-buttons {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
}

.button.primary, .button.secondary {
  font-size: 1.2rem; /* Оптимальний розмір кнопок */
  padding: 1rem 2.5rem;
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
  transition: transform 0.2s;
}

.button:hover {
  transform: translateY(-2px);
}

.button.primary {
  background-color: var(--accent-primary);
  color: white;
}

.button.secondary {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.features-section {
  padding: 3rem 0;
}

.features-section h2 {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2.2rem;
}

.features-grid {
  display: grid;
  /* Змінено на minmax(260px), щоб картки на ПК ставали 2х2 або в 4 в ряд, а не ламалися */
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem 1.5rem;
}

.feature-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  margin-bottom: 1rem;
  color: var(--accent-primary);
}

.how-to-play-section {
  padding: 3rem;
  margin-top: 3rem;
}

.how-to-play-section h2 {
  text-align: center;
  margin-bottom: 2.5rem;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--accent-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content h3 {
  margin-bottom: 0.5rem;
  color: var(--accent-primary);
}

/* 📱 Мобільні стилі (для екранів менше 768px) */
@media (max-width: 768px) {
  .hero-section h1 {
    font-size: 2.5rem;
  }

  .subtitle {
    font-size: 1.1rem;
  }

  .hero-buttons {
    flex-direction: column;
    gap: 1rem;
  }

  .button.primary, .button.secondary {
    width: 100%;
    box-sizing: border-box;
    text-align: center;
  }

  .how-to-play-section {
    padding: 1.5rem;
  }

  .step {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
</style>