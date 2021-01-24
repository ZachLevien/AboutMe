/* eslint-disable import/no-unresolved */
<template>
  <div id="home-container">
    <div id="home-container-aligned" class="container">
      <section id="home-hero" class="hero is-bold">
        <div class="hero-body">
          <div class="container">
            <h1 class="title">
              Zach Levien
            </h1>
            <h2 class="content">
              Software Engineering, Database Architect, IT Generalist
            </h2>
            <p id="press-enter" class="subtitle">
              <router-link to="/go">[press enter]</router-link>
            </p>
            <section>
              <div class="block">
                <a href="mailto:zlevien@gmail.com">
                  <b-icon pack="fas" icon="envelope"></b-icon>
                </a>
                <a href="https://www.linkedin.com/in/zachlevien/" target="_blank">
                  <b-icon pack="fab" icon="linkedin" size="is-medium"></b-icon>
                </a>
                <a href="https://github.com/ZachLevien" target="_blank">
                  <b-icon pack="fab" icon="github-square" size="is-medium"></b-icon>
                </a>
                <a href="https://twitter.com/ZachLevien" target="_blank">
                  <b-icon pack="fab" icon="twitter-square" size="is-medium"></b-icon>
                </a>
                <a href="https://www.instagram.com/zachlevien/" target="_blank">
                  <b-icon pack="fab" icon="instagram-square" size="is-medium"></b-icon>
                </a>
              </div>
            </section>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
};
</script>
