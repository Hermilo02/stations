<template>
  <div>
    <h1>Datos de la estación</h1>
    
    <!-- Mostrar el ID de la estación seleccionada -->
    <p v-if="idEstacion">ID de la estación seleccionada: {{ idEstacion }}</p>
    <p v-else>Selecciona una estación para ver los datos.</p>

    <!-- Selección de Mes y Año -->
    <div class="filters">
      <label>Mes:
        <select v-model="mesSeleccionado" @change="fetchData">
          <option v-for="(mes, index) in meses" :key="index" :value="index + 1">
            {{ mes }}
          </option>
        </select>
      </label>

      <label>Año:
        <select v-model="anioSeleccionado" @change="fetchData">
          <option v-for="anio in aniosDisponibles" :key="anio" :value="anio">
            {{ anio }}
          </option>
        </select>
      </label>
    </div>

    <!-- Tabla de datos -->
    <table v-if="datos.length">
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Temperatura</th>
          <th>Humedad</th>
          <th>Presión</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="dato in datos" :key="dato.dateutc">
          <td>{{ dato.dateutc }}</td>
          <td>{{ dato.temperatura }}</td>
          <td>{{ dato.humedad }}</td>
          <td>{{ dato.presion }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>Cargando datos o no hay información disponible.</p>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useEstacionStore } from '@/store/estacionStore';

const estacionStore = useEstacionStore();
const idEstacion = ref(estacionStore.idEstacion);
const datos = ref([]);

// Mes y Año seleccionados
const mesSeleccionado = ref(new Date().getMonth() + 1);
const anioSeleccionado = ref(new Date().getFullYear());

// Lista de meses y años disponibles
const meses = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

const aniosDisponibles = ref([]);
for (let i = new Date().getFullYear(); i >= 2020; i--) {
  aniosDisponibles.value.push(i);
}

// Función para obtener datos de la API
const fetchData = async () => {
  if (!idEstacion.value) return;

  try {
    const response = await fetch(`http://localhost:8000/estacion/${idEstacion.value}/${mesSeleccionado.value}/${anioSeleccionado.value}`);
    if (!response.ok) {
      throw new Error('Error en la respuesta del servidor');
    }
    datos.value = await response.json();
  } catch (error) {
    console.error('Error al obtener los datos de la estación:', error);
  }
};

// Escuchar cambios en la estación seleccionada
watch(() => estacionStore.idEstacion, (newId) => {
  idEstacion.value = newId;
  fetchData();
});

// Cargar datos al montar el componente si ya hay una estación seleccionada
onMounted(() => {
  if (idEstacion.value) {
    fetchData();
  }
});
</script>

<style scoped>
.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}
</style>
