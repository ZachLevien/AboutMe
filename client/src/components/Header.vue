<template>
<div class="container">
  <nav class="level">
    <p class="level-item has-text-centered">
      <a class="link is-info">skills</a>
    </p>
    <p class="level-item has-text-centered">
      <a class="link is-info">work history</a>
    </p>
    <b class="level-item has-text-centered is-size-3">
      zachlevien.us
    </b>
    <p class="level-item has-text-centered">
      <a class="link is-info">about me</a>
    </p>
    <p class="level-item has-text-centered">
      <a class="link is-info">contact</a>
    </p>
  </nav>
</div>
</template>

<script>
export default {
  name: 'Header',
  data() {
    return {
      links: [
        {
          id: 0,
          text: 'Hello world',
          page: '/HelloWorld',
        },
        {
          id: 1,
          text: 'Home',
          page: '/Home',
        },
        {
          id: 2,
          text: 'About',
          page: '/About',
        },
      ],
    };
  },
};
</script>
