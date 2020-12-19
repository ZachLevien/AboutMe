<template>
  <div id="app">
    <Nav></Nav>
    <router-view/>
  </div>
</template>

<script>
import Nav from './views/Nav.vue';

export default {
  name: 'app',
  components: {
    Nav,
  },
};
</script>

<style>
/* #app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
} */

</style>
