<template>
<div class="pure-menu pure-menu-horizontal main-nav">
    <a href="#" class="pure-menu-heading pure-menu-link">Zach Levien</a>
    <ul class="pure-menu-list">
        <li class="pure-menu-item">
            <a href="#" class="pure-menu-link">News</a>
        </li>
        <li class="pure-menu-item">
            <a href="#" class="pure-menu-link">Sports</a>
        </li>
        <li class="pure-menu-item">
            <a href="#" class="pure-menu-link">Finance</a>
        </li>
    </ul>
</div>
</template>

<script>
export default {
  name: 'Nav',
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
