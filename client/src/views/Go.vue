<template>
  <div class="Go">
    <Header/>
    <router-view/>
  </div>
</template>

<script>
import Header from '../components/Header.vue';

export default {
  name: 'Go',
  components: {
    Header,
  },
};
</script>
