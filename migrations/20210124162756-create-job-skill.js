'use strict';
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable('JobSkills', {
      jobId: {
        type: Sequelize.INTEGER,
        primaryKey: true
      },
      skillId: {
        type: Sequelize.INTEGER,
        primaryKey: true
      },
      sortOrder: {
        type: Sequelize.INTEGER
      },
      createdAt: {
        allowNull: false,
        type: Sequelize.DATE
      },
      updatedAt: {
        allowNull: false,
        type: Sequelize.DATE
      }
    })
    .then(() =>{
      return queryInterface.sequelize.query('ALTER TABLE JobSkills ADD CONSTRAINT JobSkill_pkey PRIMARY KEY (jobId, skillId)')
    });
  },
  down: async (queryInterface, Sequelize) => {
    await queryInterface.dropTable('JobSkills');
  }
};