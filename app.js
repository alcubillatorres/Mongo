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
require("dotenv").config();
const cors = require("cors");
const { ObjectID } = require("bson");

const id = process.env.ID;
const ip = process.env.IP;
var port = process.env.PORT;
var coleccion = process.env.COLECCION;
var documento = process.env.DOCUMENTO;

const url = "mongodb://" + ip + "/" + coleccion;

app.set("port", port);
app.listen(app.get("port"));
console.log("Escuchando en el puerto", port);

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
  console.log("Conectado a la base de datos", url);
});

db.on("error", (err) => {
  console.error("Error de conexión", err);
});

///////////////////////////////////////definimos los esquemas////////////////////////////////////////////////
var configuracionSchema = new mongoose.Schema({
  Id_Sitio: ObjectID,
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

var clienteSchema = new mongoose.Schema({
  Nombre: String,
  Numero: String,
});

var sitioSchema = new mongoose.Schema({
  Sitio: String,
  Key: String,
  Marca: String,
  Modelo: String,
  Cliente_id: String,
});

///////////////////////////////////////fin definimos los esquemas////////////////////////////////////////////

//////////////////////definimos el modelo en base al esquema//////////////////////////////////////////////
var Configuraciones = mongoose.model("configuraciones", configuracionSchema);
var Clientes = mongoose.model("clientes", clienteSchema);
var Sitios = mongoose.model("sitios", sitioSchema);

//////////////////////////////////////Guardamos en la bd///////////////////////////////////////////////////
app.post("/", (req, res) => {
  console.log("Buscando configuraciones del Sitio", id);
  const { TipoInterface } = req.body;
  /////////////////////////////////////////////////////guardado WAN///////////////////////////////////////////////
  if (TipoInterface === "WAN") {
    const {
      Alias,
      TipoServicio,
      TipoIP,
      DireccionIP,
      Mascara,
      Gateway,
      Vlan,
      Id_Sitio,
    } = req.body;

    var myData = new Configuraciones({
      Id_Sitio: Id_Sitio,
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

    Configuraciones.findOne(
      { Id_Sitio: Id_Sitio },
      async function (err, newServicios) {
        if (newServicios) {
          //actualizamos la configuración

          await Configuraciones.updateOne(
            { Id_Sitio: newServicios.Id_Sitio },
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
      }
    );
  } else {
    ///////////////////////////////////////////////Guardado LAN/////////////////////////////////////////////////
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
      Id_Sitio,
    } = req.body;

    var myData = new Configuraciones({
      Id_Sitio: Id_Sitio,
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

    Configuraciones.findOne(
      { Id_Sitio: Id_Sitio },
      async function (err, newServicios) {
        if (newServicios) {
          await Configuraciones.updateOne(
            { Id_Sitio: newServicios.Id_Sitio },
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
      }
    );
  }
});

//////////////////////////consultamos las wan/lan del sitio existente//////////////////////////////////////
app.get("/configuracion", (req, res) => {
  console.log("Buscando la Configuración del Sitio", req.query.id);
  const Id_Sitio=  req.query.id

  Configuraciones.findOne({ Id_Sitio: Id_Sitio},
 
    async function (err, newServicios) {
      if (newServicios) {
        res.status(200);
        res.send(newServicios);
      } else{
        res.status(201)
        res.send("No se encontraron datos")
      }
      if (err) {
        return err;
      }
    }
  );

  
});
//////////////////////////fin consulta las wan/lan del sitio existente/////////////////////////////////////////





////////////////////////////////Guardado Ruteo //////////////////////////////////////////////////////

app.post("/rutas", (req, res) => {
  const { Alias, Default, Red, Mascara, Gateway, Prioridad } = req.body;

  var myData = new Configuraciones({
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

  Configuraciones.findOne({ _id: id }, "_id", async function (err, newServicios) {
    if (newServicios) {
      //actualizamos el servicio

      await Configuraciones.updateOne(
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
                Prioridad: Prioridad,
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
////////////////////////////////Fin Guardado Ruteo //////////////////////////////////////////////////////

//////////////////////////consulta Clientes//////////////////////////////////////
app.get("/clientes", (req, res) => {
  console.log("Buscando clientes");
  Clientes.find(async function (err, newClientes) {
    if (newClientes) {
      res.send(newClientes);
    }
    if (err) {
      return err;
    }
  });
});

//////////////////////////fin consulta Clientes/////////////////////////////////////////

///////////////////////////inicio guardado Clientes/////////////////////////////////////////

app.post("/clientes", (req, res) => {
  const { Nombre, Numero } = req.body;

  var myData = new Clientes({
    Nombre,
    Numero,
  });

  Clientes.findOne(
    { Nombre: Nombre },
    "Nombre",
    async function (err, newClientes) {
      if (newClientes) {
        res.status(200);
        console.log("El cliente ya se encontraba en la BD");
        const { _id } = newClientes;
        res.send(newClientes);
      } else {
        //Elemento nuevo en la bd
        myData
          .save()
          .then((user) => {
            res.status(200);
            res.send(user);
            console.log("Cliente Agregado exitosamente");
          })
          .catch((err) => {
            console.log(err);
            res.send(400, "Bad Request");
          });
      }
      if (err) {
        return err;
      }
    }
  );
});

//////////////////////////fin guardado Clientes/////////////////////////////////////////

///////////////////////////inicio guardado sitios////////////////////////////////////////
app.post("/sitios", (req, res) => {
  const { Sitio, Key, Cliente_id, Marca, Modelo } = req.body;
  
  console.log("alta sitio", Cliente_id)
  var myData = new Sitios({
    Sitio,
    Key,
    Marca,
    Modelo,
    Cliente_id,
  });

  

    myData
      .save()
      .then((sitio) => {
        res.status(200);
        res.send(sitio._id);
        console.log("Sitio Agregado Exitosamente", sitio._id);
      }).catch((error) => {
        console.log(error);
        res.send(400, "Bad Request");
      });
 
});

//////////////////////////fin guardado sitios/////////////////////////////////////////

///////////////////////////inicio consulta de  sitios////////////////////////////////////////
app.get("/sitios", (req, res) => {
  console.log("Buscando los sitios del cliente", req.query.id);
  Sitios.find({ Cliente_id: req.query.id }).then(
    (sitio) => {
      if (sitio) {
        res.send(sitio);
      }
    },
    (e) => {
      res.status(400).send(e);
    }
  );
});
//////////////////////////fin consulta de  sitios/////////////////////////////////////////
