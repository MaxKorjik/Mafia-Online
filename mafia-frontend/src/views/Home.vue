<template>
  <div class="home-container">
    <!-- Главный газетный заголовок / Banner -->
    <header class="newspaper-header">
      <div class="edition-tag">СПЕЦІАЛЬНИЙ ВИПУСК — ЧИКАГО, 1932</div>
      <h1 class="main-title">МАФІЯ ОНЛАЙН</h1>
      <p class="subtitle">Секретні досьє, нічні змови та боротьба за контроль над містом</p>
      
      <div class="hero-buttons">
        <router-link to="/rooms" class="button primary">ДОЛУЧИТИСЯ ДО ГРИ</router-link>
        <router-link to="/leaderboard" class="button secondary">ТАБЛИЦЯ ЛІДЕРІВ</router-link>
      </div>
    </header>

    <hr class="newspaper-hr" />

    <!-- Газетные колонки / Особливості -->
    <section class="features-section">
      <h2 class="section-title">ОСОБЛИВОСТІ РЕЖИМУ</h2>
      <div class="features-grid">
        <article class="feature-card">
          <div class="badge-num">I</div>
          <h3>МУЛЬТИПЛЕЄР</h3>
          <p>Живі сесії через захищеный протокол. Безпека зв'язку та миттєва передача даних між кабінетами.</p>
        </article>

        <article class="feature-card">
          <div class="badge-num">II</div>
          <h3>РОЗПОДІЛ РОЛЕЙ</h3>
          <p>Класична таємна видача досьє: Мафія, Дон, Комісар, Лікар та Мирні жителі.</p>
        </article>

        <article class="feature-card">
          <div class="badge-num">III</div>
          <h3>ЗАЛ СУДУ</h3>
          <p>Захищений текстовий канал для обговорення слідів, аргументів та проведення щоденного голосування.</p>
        </article>

        <article class="feature-card">
          <div class="badge-num">IV</div>
          <h3>РЕЙТИНГ БЮРО</h3>
          <p>Фіксація всіх успішних розслідувань та ліквідацій у загальноміському табелі заслуживших.</p>
        </article>
      </div>
    </section>

    <!-- Секция планов развития (Сторителлинг) -->
    <section class="roadmap-section">
      <div class="roadmap-card">
        <div class="roadmap-header">
          <span class="status-tag">В РОЗРОБЦІ</span>
          <h2>ПЛАНЫ ГОЛОВНОГО УПРАВЛІННЯ</h2>
        </div>
        <p class="roadmap-text">
          Наразі доступний <strong>Класичний режим</strong> мафії. Проте аналітичний відділ вже готує масштабне оновлення — 
          <strong>Режим з поглибленим сторітелінгом та персонажами</strong>. На гравців чекають унікальні передісторії, 
          персональні сюжетні квести та розширений вибір тактичних дій під час нічної фази.
        </p>
      </div>
    </section>

    <!-- Инструкция / Як грати -->
    <section class="how-to-play-section">
      <h2 class="section-title">ПРОТОКОЛ ВСТУПУ</h2>
      <div class="steps-grid">
        <div class="step">
          <div class="step-number">01</div>
          <div class="step-content">
            <h3>РЕЄСТРАЦІЯ</h3>
            <p>Авторизуйтесь у системі бюро та отримайте шифр оперативника.</p>
          </div>
        </div>

        <div class="step">
          <div class="step-number">02</div>
          <div class="step-content">
            <h3>ПОШУК КІМНАТИ</h3>
            <p>Оберіть вільну явочну квартиру або створіть власний стол.</p>
          </div>
        </div>

        <div class="step">
          <div class="step-number">03</div>
          <div class="step-content">
            <h3>ОТРИМАННЯ ДОСЬЄ</h3>
            <p>Ознайомтеся зі своєю таємною роллю до настання першої ночі.</p>
          </div>
        </div>

        <div class="step">
          <div class="step-number">04</div>
          <div class="step-content">
            <h3>ПОЧАТОК СЛІДСТВА</h3>
            <p>Дезинформуйте ворогів, захищайте союзників та викривайте мафію.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
  color: var(--ink-color);
  font-family: var(--font-text);
}

/* 📰 Газетная шапка */
.newspaper-header {
  text-align: center;
  padding: 2rem 0;
}

.edition-tag {
  font-size: 0.85rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  border-bottom: 1px solid var(--ink-color);
  display: inline-block;
  padding-bottom: 4px;
  margin-bottom: 1rem;
  opacity: 0.8;
}

.main-title {
  font-family: var(--font-title);
  font-size: 3.8rem;
  letter-spacing: 1px;
  margin: 0.5rem 0;
  text-transform: uppercase;
  color: var(--ink-color);
}

.subtitle {
  font-size: 1.2rem;
  font-style: italic;
  margin-bottom: 2rem;
  opacity: 0.85;
}

.hero-buttons {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
}

.button {
  font-family: var(--font-text);
  font-size: 0.95rem;
  font-weight: bold;
  padding: 0.8rem 1.8rem;
  text-decoration: none;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: all 0.2s ease;
  border-radius: 0; /* Острые газетные углы */
}

.button.primary {
  background-color: var(--ink-color);
  color: var(--paper-color);
  border: 1px solid var(--ink-color);
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.4);
}

.button.primary:hover {
  background-color: transparent;
  color: var(--ink-color);
}

.button.secondary {
  background-color: transparent;
  color: var(--ink-color);
  border: 1px solid var(--ink-color);
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.4);
}

.button.secondary:hover {
  background-color: var(--ink-color);
  color: var(--paper-color);
}

/* Разделительная черта в газетном стиле */
.newspaper-hr {
  border: 0;
  border-top: 2px solid var(--ink-color);
  border-bottom: 1px solid var(--ink-color);
  height: 3px;
  margin: 2.5rem 0;
}

/* 🏛 Секция заголовков */
.section-title {
  font-family: var(--font-title);
  text-align: center;
  font-size: 1.8rem;
  letter-spacing: 1px;
  margin-bottom: 2rem;
  text-transform: uppercase;
}

/* 📋 Сетка карточек */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  border: 1px solid var(--ink-color);
  padding: 1.5rem;
  background: var(--paper-color);
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.3);
  position: relative;
}

.badge-num {
  font-family: var(--font-title);
  font-size: 1.2rem;
  font-weight: bold;
  opacity: 0.5;
  margin-bottom: 0.5rem;
}

.feature-card h3 {
  font-family: var(--font-title);
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  letter-spacing: 0.5px;
}

.feature-card p {
  font-size: 0.9rem;
  line-height: 1.4;
  opacity: 0.85;
}

/* 📜 Планы развития (Сторителлинг) */
.roadmap-section {
  margin: 3rem 0;
}

.roadmap-card {
  border: 2px dashed var(--ink-color);
  padding: 2rem;
  background: rgba(0, 0, 0, 0.03);
}

.roadmap-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.status-tag {
  font-size: 0.75rem;
  font-weight: bold;
  background: var(--ink-color);
  color: var(--paper-color);
  padding: 3px 8px;
  letter-spacing: 1px;
}

.roadmap-card h2 {
  font-family: var(--font-title);
  font-size: 1.4rem;
  margin: 0;
}

.roadmap-text {
  font-size: 0.95rem;
  line-height: 1.6;
}

/* 👣 Инструкция / Шаги */
.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.step {
  border-left: 2px solid var(--ink-color);
  padding-left: 1rem;
}

.step-number {
  font-family: var(--font-title);
  font-size: 1.4rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
  opacity: 0.6;
}

.step-content h3 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.step-content p {
  font-size: 0.85rem;
  line-height: 1.4;
  opacity: 0.85;
}

/* 📱 Адаптив */
@media (max-width: 768px) {
  .main-title {
    font-size: 2.4rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .hero-buttons {
    flex-direction: column;
    gap: 0.8rem;
  }

  .button {
    width: 100%;
    text-align: center;
    box-sizing: border-box;
  }

  .roadmap-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>