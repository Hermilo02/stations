import { defineStore } from 'pinia';

export const useEstacionStore = defineStore('estacion', {
  state: () => ({
    idEstacion: null,
  }),
  actions: {
    setEstacion(id) {
      this.idEstacion = id;
    },
  },
});
