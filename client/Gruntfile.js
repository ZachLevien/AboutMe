module.exports = function(grunt) {
  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
      },
      build: {
        src: 'src/<%= pkg.name %>.js',
        dest: 'build/<%= pkg.name %>.min.js',
      },
    },
    pure_grids: {
      dest: 'build/public/css/main-grid.css',
      options: {
        units: 12, // 12-column grid
        mediaQueries: {
          sm: 'screen and (min-width: 35.5em)', // 568px
          md: 'screen and (min-width: 48em)', // 768px
          lg: 'screen and (min-width: 64em)', // 1024px
          xl: 'screen and (min-width: 80em)', // 1280px
        },
      },
    },
  });

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-pure-grids');

  // Default task(s).
  grunt.registerTask('default', ['uglify']);
};
