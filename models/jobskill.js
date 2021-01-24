'use strict';
const {
  Model
} = require('sequelize');
module.exports = (sequelize, DataTypes) => {
  class JobSkill extends Model {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
    static associate(models) {
      this.myAssociation = this.hasMany(models.Job);
      this.myAssociation = this.hasMany(models.Skill);
    }
  };
  JobSkill.init({
    jobId: DataTypes.INTEGER,
    skillId: DataTypes.INTEGER,
    sortOrder: DataTypes.INTEGER
  }, {
    sequelize,
    modelName: 'JobSkill',
  });
  return JobSkill;
};