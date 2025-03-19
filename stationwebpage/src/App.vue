<template>
  <div>
    <LayoutHeader />
    <router-view />
  </div>
</template>

<script>
import LayoutHeader from './components/LayoutHeader.vue';

export default {
  name: 'App',
  components: {
    LayoutHeader
  }
}
</script>


<style>
</style>
