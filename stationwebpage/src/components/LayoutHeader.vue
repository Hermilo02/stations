<template>
  <nav class="navbar" role="navigation">
    <div class="logo">MiApp</div>
    <ul class="nav-links">
      <li>
        <router-link to="/" active-class="active" aria-current="page">
          Inicio
        </router-link>
      </li>
      <li>
        <router-link to="/Graphic" active-class="active">
          Graficas
        </router-link>
      </li>
      <li>
        <router-link to="/Table" active-class="active">
          Tablas
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script setup>
// No se requiere lógica específica para este componente básico
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #64ccfc;
  padding: 1rem 2rem;
  color: #000000;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 1rem;
  padding: 0;
  margin: 0;
}

.nav-links a {
  color: #000000;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  transition: background 0.3s ease;
}

.nav-links a:hover,
.nav-links .active {
  background-color: #00b9aa;
  font-weight: bold;
  border-bottom: 2px solid #080055;
}
</style>
