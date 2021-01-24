const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const morgan = require('morgan');
const { Sequelize } = require('sequelize');

const app = express();

app.use(morgan('tiny'));
app.use(cors());
app.use(bodyParser.json())

app.get('/', (req,res) => {
    res.json({
        message: 'This is the way.'
    });
});

const port = process.env.PORT || 4000;
app.listen(port, () => {
    console.log(`Listening on ${port}`);
});