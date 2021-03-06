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
var {PythonShell} = require('python-shell')

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
  console.log("Conectado a la Base de Datos:", url);
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
  Scripts: [
    {
      Nombre: String,
    }
  ]
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

///////////////////////////////////////fin definimos los esquemas/////////////////////////////////////////

//////////////////////definimos el modelo en base al esquema//////////////////////////////////////////////
var Configuraciones = mongoose.model("configuraciones", configuracionSchema);
var Clientes = mongoose.model("clientes", clienteSchema);
var Sitios = mongoose.model("sitios", sitioSchema);

//////////////////////////////////////Guardado de las configuraciones//////////////////////////////////////
app.post("/configuraciones", (req, res) => {
  console.log("Buscando Configuraciones existentes del Sitio", req.body.Id_Sitio);
  const { TipoInterface } = req.body;
  console.log("Tipo interface", TipoInterface)


  /////////////////////////////////////////////////////Guardado WAN/////////////////////////////////////////
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
          //actualizamos la configuración en caso de encontrar registro existente
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
          Configuraciones.findOne(
            { Id_Sitio: Id_Sitio },
            async function (err, newServicios) {
              if (newServicios) {
                console.log("¡Wan Agregada!")
                res.status(200);
                res.send(newServicios);
              }
              if (err) {
              return err;
              }
          });
        } else {
          //Elemento nuevo en la BD
          myData
          .save()
          .then((user) => {
            res.status(200);
            res.send(user);
            console.log("¡Wan Agregada!");
          })
          .catch((err) => {
            console.log(err);
            res.send(400, "Bad Request");
          });
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
      async function (err, newConfiguracion) {
        if (newConfiguracion) {
          await Configuraciones.updateOne(
            { Id_Sitio: newConfiguracion.Id_Sitio },
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
          Configuraciones.findOne(
            { Id_Sitio: Id_Sitio },
            async function (err, newServicios) {
              if (newServicios) {
                console.log("¡Lan Agregada!")
                res.status(200);
                res.send(newServicios);
              }
              if (err) {
              return err;
              }
          });
        } else {
          //Elemento nuevo en la bd
          myData
          .save()
          .then((user) => {
            res.status(200);
            res.send(user);
            console.log("¡Lan Agregada!");
          })
          .catch((err) => {
            console.log(err);
            res.send(400, "Bad Request");
          });
        }

      }
    );
  }
});
//////////////////////////////////////Fin guardado de las configuraciones///////////////////////////////////

//////////////////////////Consulta de Wan/Lan de un sitio existente////////////////////////////////////////
app.get("/configuraciones", (req, res) => {
  console.log("Buscando la Configuración del Sitio:", req.query.Id_Sitio);
  const  Id_Sitio =  req.query.Id_Sitio
  Configuraciones.findOne({ Id_Sitio: Id_Sitio},
    async function (err, newServicios) {
      if (newServicios !== null) {
        res.status(200);
        res.send(newServicios);
      } else{
        res.status(201)
        res.send("No se encontraron Configuraciones")
      }
      if (err) {
        return err;
      }
    }
  );
});
//////////////////////////Fin consulta de Wan/Lan de un sitio existente///////////////////////////////


////////////////////////////////Guardado Ruteo////////////////////////////////////////////////////////
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

//////////////////////////Consulta de Clientes//////////////////////////////////////////////////////////
app.get("/clientes", (req, res) => {
  console.log("Buscando clientes....");
  try{
    Clientes.find(function(e, clientes){
      if(clientes){
        res.send(clientes)
      }
    })
  }catch (e) {
    next(e)
  }
});
//////////////////////////Fin consulta de Clientes//////////////////////////////////////////////////////

///////////////////////////Guardado de Clientes/////////////////////////////////////////////////////
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
        console.log("El cliente ya se encontraba guardado");
        const { _id } = newClientes;
        res.send(newClientes);
      } else {
        //Elemento nuevo en la bd
        myData
          .save()
          .then((user) => {
            res.status(200);
            res.send(user);
            console.log("¡Cliente Agregado exitosamente!");
          })
          .catch((err) => {
            console.log(err);
            res.status(400).send("Bad Request")
          });
      }
      if (err) {
        return err;
      }
    }
  );
});
//////////////////////////Fin guardado de Clientes/////////////////////////////////////////////////////

///////////////////////////Guardado de Sitios/////////////////////////////////////////////////////////
app.post("/sitios", (req, res) => {
  const { Sitio, Key, Cliente_id, Marca, Modelo } = req.body;
  console.log("Dando de Alta el Sitio:", Cliente_id)

  var myData = new Sitios({
    Sitio,
    Key,
    Marca,
    Modelo,
    Cliente_id,
  });


  Sitios
  .findOne({Sitio: Sitio, Key: Key})
    .exec(
    async function (err, newSitio) {
      console.log(newSitio)
      if (newSitio) {
        console.log("¡Sitio Existente!")
        res.status(200);
        res.send(newSitio);
      }else {
        //Elemento nuevo en la BD
        myData
        .save()
        .then((sitio) => {
          res.status(200);
          res.send(sitio._id);
          console.log("¡Sitio Agregado Exitosamente!", sitio._id);
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
    )
  

});
//////////////////////////Fin guardado de sitios//////////////////////////////////////////////////////

///////////////////////////Consulta de Sitios/////////////////////////////////////////////////////////
app.get("/sitios", (req, res) => {
  console.log("Buscando los sitios del cliente:", req.query.id);
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
//////////////////////////Fin consulta de Sitios//////////////////////////////////////////////////////

app.get("/python", (req, res) => {
  const Id_Sitio = req.body.Id_Sitio;

  console.log("Ejecutando python");

   

   /*  const ls = spawn('py', ['config.py']);
 
    ls.on('close', (code) => {
      console.log(`child process exited with code ${code}`);
      res.send({message: 'Finalizo'});
    });
 */
    
    
    // res.sendFile(__dirname +'/configuracion.txt')

 
});


app.post("/archivo", (req, res) => {
 
  const {nombre, Id_Sitio, key, NombreCliente, Modelo} = req.body;

  const fileName = "ARCHIVO_DE_CONFIG_"+nombre
  console.log("Guardando archivo", fileName);

  var myData = new Configuraciones({
    Id_Sitio: Id_Sitio,
    Scripts: [
      {
        Nombre: String,
      }
    ]
  });
  try{
    Configuraciones.findOne(
      { Id_Sitio: Id_Sitio },
      async function (err, newConfiguracion){
        if(newConfiguracion){
          await Configuraciones.updateOne(
            {Id_Sitio: newConfiguracion.Id_Sitio},
            {
              $addToSet: {
                Scripts: [
                  {
                    Nombre: fileName,
                  }
                ]
              }
            }
          )
        }else{
          myData.save()
          .then((config)=>{
            console.log("Archivo agregado")
          })
        }
      }
    )
  } catch (error) {
    console.log(error)
    return next(error)
  }

  var options = {
    mode: 'text',
    args: [nombre, Id_Sitio, NombreCliente, Modelo, key]
  };

  PythonShell.run('configuracion.py', options, function (err, results) {
    if (err) 
      throw err;
    // Results is an array consisting of messages collected during execution
    //console.log('results: %j', results);
    res.sendFile(__dirname +"/txt/"+fileName)
  });
 
});