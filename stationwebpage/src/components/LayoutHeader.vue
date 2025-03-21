<template>
  <div class="app-container">
    <!-- Navbar -->
    <nav class="navbar">
      <div class="nav-left">
        <div class="logo">Estaciones</div>
        <ul class="nav-links">
          <li>
            <router-link to="/" active-class="active">
              Inicio
            </router-link>
          </li>
          <li>
            <router-link to="/Graphic" active-class="active">
              Gráficas
            </router-link>
          </li>
          <li>
            <router-link to="/Table" active-class="active">
              Tablas
            </router-link>
          </li>
        </ul>

        <!-- Menú de estaciones como select -->
        <div class="stations-menu">
          <select v-model="selectedEstacion" @change="guardarEstacion">
            <!-- Opción por defecto -->
            <option value="" disabled selected>Selecciona una estación</option>
            <!-- Lista de estaciones -->
            <option v-for="estacion in estaciones" :key="estacion.id_station" :value="estacion.id_station">
              {{ estacion.nombre }}
            </option>
          </select>
        </div>
      </div>

      <!-- Icono del menú lateral -->
      <div class="menu-icon" @click="toggleSidebar">
        <span :class="{ open: isMenuOpen }"></span>
        <span :class="{ open: isMenuOpen }"></span>
        <span :class="{ open: isMenuOpen }"></span>
      </div>
    </nav>

    <!-- Menú desplegable lateral -->
    <div class="sidebar" :class="{ 'show-sidebar': isMenuOpen }">
      <router-link to="/settings" class="sidebar-link">Configuración</router-link>
      <router-link to="/profile" class="sidebar-link">Perfil</router-link>
      <router-link to="/help" class="sidebar-link">Ayuda</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useEstacionStore } from '@/store/estacionStore'; // Importar el store de Pinia

const estacionStore = useEstacionStore(); // Instancia de Pinia

// Estado para el menú lateral
const isMenuOpen = ref(false);

// Estado para el menú desplegable de estaciones
const estaciones = ref([]);
const selectedEstacion = ref(estacionStore.idEstacion || ""); // Cargar el ID almacenado si existe

// Función para alternar el estado del menú lateral
const toggleSidebar = () => {
  isMenuOpen.value = !isMenuOpen.value;
};

// Cargar las estaciones al montar el componente
onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/estaciones');
    if (!response.ok) {
      throw new Error('Error en la respuesta del servidor');
    }
    const data = await response.json();
    estaciones.value = data;
  } catch (error) {
    console.error('Error al obtener las estaciones:', error);
  }
});

// Guardar la estación seleccionada en Pinia
const guardarEstacion = () => {
  estacionStore.setEstacion(selectedEstacion.value);
};
</script>

<style scoped>
.app-container {
  display: flex;
  width: 100%;
}

/* Navbar */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #505050;
  padding: 1rem 2rem;
  color: #ffffff;
  width: 100%;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 2rem;
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
  color: #ffffff;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  transition: background 0.3s ease;
}

.nav-links a:hover,
.nav-links .active {
  color: #5999fa;
  font-weight: bold;
  border-bottom: 2px solid #74e3ff;
}

/* Menú */
.menu-icon {
  display: flex;
  flex-direction: column;
  gap: 5px;
  cursor: pointer;
}

.menu-icon span {
  width: 25px;
  height: 3px;
  background-color: #ffffff;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.menu-icon span.open:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.menu-icon span.open:nth-child(2) {
  opacity: 0;
}

.menu-icon span.open:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

/* Sidebar (menú lateral fijo) */
.sidebar {
  position: fixed;
  top: 65px;
  right: -250px;
  /* Oculto por defecto */
  width: 250px;
  height: 100%;
  background-color: #505050;
  padding: 2rem 1rem;
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.2);
  transition: right 0.3s ease;
}

.sidebar.show-sidebar {
  right: 0;
}

.sidebar-link {
  display: block;
  color: #fff;
  text-decoration: none;
  padding: 1rem 0;
  border-bottom: 1px solid #fff;
}

.sidebar-link:hover {
  color: #5999fa;
}

/* Estaciones */
.stations-menu {
  margin-top: 1rem;
  color: #fff;
}

.stations-menu select {
  width: 100%;
  padding: 0.5rem;
  background-color: #fff;
  color: #505050;
  border-radius: 5px;
  border: 1px solid #74e3ff;
  transition: background-color 0.3s ease;
}

.stations-menu select:hover {
  background-color: #f0f0f0;
}

/* Contenido principal */
.main-content {
  flex-grow: 1;
  padding: 2rem;
  transition: margin-right 0.3s ease;
}

.main-content.shifted {
  margin-right: 250px;
  /* Se ajusta cuando el menú está abierto */
}
</style> 