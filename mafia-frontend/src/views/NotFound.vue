<template>
  <div class="not-found">
    <h1>404</h1>
    <h2>Сторінку не знайдено</h2>
    <p>Вибачте, але сторінка, яку ви шукаєте, не існує.</p>
    <router-link to="/" class="btn">Повернутися на головну</router-link>
  </div>
</template>

<script setup>
// Компонент не потребує логіки
</script>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: 2rem;
}

h1 {
  font-size: 6rem;
  margin: 0;
  color: var(--primary-color);
}

h2 {
  font-size: 2rem;
  margin: 1rem 0;
}

p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: var(--text-secondary);
}

.btn {
  display: inline-block;
  padding: 0.8rem 2rem;
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.btn:hover {
  background-color: var(--primary-color-dark);
}
</style> 