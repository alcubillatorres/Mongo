/* MongoDB es una base de datos que almacena sus datos como documentos. 
Lo más común es que estos documentos se parezcan a una estructura similar a JSON 
Uno de los factores clave con MongoDB es su flexibilidad cuando se trata de estructura. 
las propiedades de un documento en esta bd no son necesarias en todos los documentos que forman parte de la colección
Esto es lo que hace que MongoDB sea muy diferente de una base de datos SQL
que requiere un esquema de base de datos fuertemente definido de cada objeto que almacena.

Express posee métodos para especificar que función ha de ser llamada dependiendo del verbo HTTP usado en la petición
(GET, POST, SET, etc.) 

Mongoose contiene muchas funciones diferentes que nos permiten validar, guardar, eliminar y consultar 
los datos utilizando las funciones comunes de MongoDB.*/

var express = require("express");
var app = express();
const mongoose = require("mongoose");
require('dotenv').config();
const cors = require("cors");

const id = process.env.ID
const ip = process.env.IP
var port = process.env.PORT
var coleccion = process.env.COLECCION
var documento = process.env.DOCUMENTO
const url = "mongodb://"+ip+"/"+coleccion   



app.set("port", port);
app.listen(app.get("port"));
console.log("Listen on port", port);

app.use(express.json());

app.use(
  cors({
    origin: function (origin, callback) {
      return callback(null, true);
    },
    optionsSuccessStatus: 200,
    credentials: true,
  })
);

app.use(function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  next();
});

app.use(express.urlencoded({ extended: true })); //converts request body to JSON
app.use(express.static("public")); //para usar la carpeta public con una ruta estática

//Nos conectamos a la bd
mongoose.connect(url, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  useFindAndModify: false,
  useCreateIndex: true,
});

mongoose.Promise = global.Promise;

var db = mongoose.connection;
db.once("open", (_) => {
  console.log("Database connected:", url);
});

db.on("error", (err) => {
  console.error("connection error:", err);
});

///////////////////////////////////////definimos el esquema////////////////////////////////////////////////
var perfilSchema = new mongoose.Schema({
  Wan: [
    {
      TipoInterface: String,
      Alias: String,
      TipoServicio: String,
      TipoIP: String,
      DireccionIP: String,
      Mascara: String,
      Gateway: String,
      Vlan: Number,
    },
  ],

  Lan: [
    {
      TipoInterface: String,
      LanAlias: String,
      LanDireccionIP: String,
      LanMascara: String,
      LanVlan: Number,
      LanDHCP: String,
      DHCPFrom: String,
      DHCPTo: String,
      LanServidorDNS1: String,
      LanServidorDNS2: String,
    },
  ],
  Rutas: [
    {
      Default: Boolean,
      Red: String,
      Mascara: String,
      Gateway: String,
      Prioridad: Number,
      Alias: String,
    },
  ],
});
///////////////////////////////////////fin definimos el esquema////////////////////////////////////////////

//////////////////////definimos el modelo en base al esquema//////////////////////////////////////////////
var Servicios = mongoose.model(documento, perfilSchema);

//////////////////////////////////////Guardamos en la bd///////////////////////////////////////////////////
app.post("/", (req, res) => {
  
  console.log("buscando actualizar" , id)
  const { TipoInterface } = req.body;
  /////////////////////////////////////////////////////guardado WAN///////////////////////////////////////////////
  if (TipoInterface === "WAN") {
    const { Alias, TipoServicio, TipoIP, DireccionIP, Mascara, Gateway, Vlan} =
      req.body;

    var myData = new Servicios({
      Wan: [
        {
          TipoInterface: TipoInterface,
          Alias: Alias,
          TipoServicio: TipoServicio,
          TipoIP: TipoIP,
          DireccionIP: DireccionIP,
          Mascara: Mascara,
          Gateway: Gateway,
          Vlan: Vlan,
        },
      ],
    });

    Servicios.findOne({ _id: id }, "_id", async function (err, newServicios) {
      
      if (newServicios) {
        //actualizamos el servicio

        await Servicios.updateOne(
          { _id: newServicios._id },
          {
            $addToSet: {
              Wan: [
                {
                  TipoInterface: TipoInterface,
                  Alias: Alias,
                  TipoServicio: TipoServicio,
                  TipoIP: TipoIP,
                  DireccionIP: DireccionIP,
                  Mascara: Mascara,
                  Gateway: Gateway,
                  Vlan: Vlan,
                },
              ],
            },
          }
        );
        res.status(200);
        res.send("Agregado con éxito");
      } else {
        //Elemento nuevo en la bd
        myData.save(function (err, myData) {
          if (err) return res.status(500).send(err);
          res.status(200);
          res.send("Exito");
          console.log("Save");
        });
      }

      if (err) {
        return err;
      }
    });
  } else {
    ///////////////////////////////////////////////guardado LAN/////////////////////////////////////////////////
    const {
      LanAlias,
      LanDireccionIP,
      LanMascara,
      LanVlan,
      LanDHCP,
      DHCPFrom,
      DHCPTo,
      LanServidorDNS1,
      LanServidorDNS2,
    } = req.body;

    var myData = new Servicios({
      Lan: [
        {
          TipoInterface: TipoInterface,
          LanAlias: LanAlias,
          LanDireccionIP: LanDireccionIP,
          LanMascara: LanMascara,
          LanVlan: LanVlan,
          LanDHCP: LanDHCP,
          DHCPFrom: DHCPFrom,
          DHCPTo: DHCPTo,
          LanServidorDNS1: LanServidorDNS1,
          LanServidorDNS2: LanServidorDNS2,
        },
      ],
    });

    Servicios.findOne({ _id: id }, "_id", async function (err, newServicios) {
      if (newServicios) {
        await Servicios.updateOne(
          { _id: newServicios._id },
          {
            $addToSet: {
              Lan: [
                {
                  TipoInterface: TipoInterface,
                  LanAlias: LanAlias,
                  LanDireccionIP: LanDireccionIP,
                  LanMascara: LanMascara,
                  LanVlan: LanVlan,
                  LanDHCP: LanDHCP,
                  DHCPFrom: DHCPFrom,
                  DHCPTo: DHCPTo,
                  LanServidorDNS1: LanServidorDNS1,
                  LanServidorDNS2: LanServidorDNS2,
                },
              ],
            },
          }
        );
        res.status(200);
        res.send("Agregado con éxito");
      } else {
        //Elemento nuevo en la bd
        myData.save(function (err, myData) {
          if (err) return res.status(500).send(err);
          res.status(200);
          res.send("Exito");
          console.log("Save");
        });
      }
      if (err) {
        return err;
      }
    });
  }
});

//////////////////////////consultamos las wan/lan del cliente//////////////////////////////////////
app.get("/", (req, res) => {
  console.log("Buscando el servicio", req.query.id);
  Servicios.findOne({ _id: req.query.id }).then(
    (cliente) => {
      if (cliente) {
        res.send(cliente);
      }
    },
    (e) => {
      res.status(400).send(e);
    }
  );
});
//////////////////////////fin consulta las wan/lan del cliente/////////////////////////////////////////

////////////////////////////////guardado Ruteo //////////////////////////////////////////////////////

app.post("/rutas", (req, res) => {
  
  const { Alias, Default, Red, Mascara, Gateway, Prioridad } = req.body;

  var myData = new Servicios({
    Rutas: [
      {
        Alias: Alias,
        Default: Default,
        Red: Red,
        Mascara: Mascara,
        Gateway: Gateway,
        Prioridad: Prioridad,
      },
    ],
  });

  Servicios.findOne({ _id: id }, "_id", async function (err, newServicios) {
    if (newServicios) {
      //actualizamos el servicio

      await Servicios.updateOne(
        { _id: newServicios._id },
        {
          $addToSet: {
            Rutas: [
              {
                Alias: Alias,
                Default: Default,
                Red: Red,
                Mascara: Mascara,
                Gateway: Gateway,
                Prioridad: Prioridad
              },
            ],
          },
        }
      );
      res.status(200);
      res.send("Agregado con éxito");
    } else {
      //Elemento nuevo en la bd
      myData.save(function (err, myData) {
        if (err) return res.status(500).send(err);
        res.status(200);
        res.send("Exito");
        console.log("Save");
      });
    }

    if (err) {
      return err;
    }
  });
});
