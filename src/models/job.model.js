const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
    sequelize.define('job',{
        id: {
            allowNull: false,
            autoIncrement: true,
            primaryKey: true,
            type: DataTypes.INTEGER
        },
        title: {
			allowNull: false,
			type: DataTypes.STRING,
        },
        desc: {
			allowNull: false,
			type: DataTypes.STRING,
        },
        company: {
			allowNull: false,
			type: DataTypes.STRING,
        },
        start_date: {
			allowNull: false,
			type: DataTypes.DATEONLY,
        },
        end_date: {
			allowNull: false,
			type: DataTypes.DATEONLY,
        },
        created_at: {
			allowNull: false,
			type: DataTypes.DATE,
        },
        created_by: {
			allowNull: false,
			type: DataTypes.string,
		},
        updated_at: {
			allowNull: false,
			type: DataTypes.DATE,
        },
        deleted_at: {
			allowNull: false,
			type: DataTypes.DATE,
		},
    });
};