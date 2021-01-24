const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
    sequelize.define('skill',{
        id: {
            allowNull: false,
            autoIncrement: true,
            primaryKey: true,
            type: DataTypes.INTEGER
        },
        desc: {
			allowNull: false,
			type: DataTypes.STRING,
        },
        logo: {
			allowNull: false,
			type: DataTypes.STRING,
        },        
        created_at: {
			allowNull: false,
			type: DataTypes.DATE,
        },
        created_by: {
			allowNull: false,
			type: DataTypes.STRING,
		},
        updated_at: {
			allowNull: false,
			type: DataTypes.DATE,
        },
        updated_by: {
			allowNull: false,
			type: DataTypes.STRING,
		},
        deleted_at: {
			allowNull: false,
			type: DataTypes.DATE,
		},
    });
};