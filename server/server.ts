import { SQLDataSource } from "datasource-sql";

import { ApolloServer as ApolloServerExpress } from "apollo-server-express";
import { Application } from "express";
import resolvers from "./resolvers";
import schema from "./schema";
import { knexConfig } from "./db";
import knex from "knex";

const express = require("express");

const db = new SQLDataSource(knexConfig);

export interface Context {
  dataSources: { db: { knex: knex; db: knex } };
}

const app: Application = express();
const path = "/";
app.set("port", process.env.PORT || 4000);
const server = new ApolloServerExpress({
  typeDefs: schema,
  resolvers: resolvers as any,
  playground: true,
  introspection: true,
  tracing: true,
  dataSources: () => ({ db }),
  // plugins: [responseCachePlugin()],
  // cacheControl: {
  //   defaultMaxAge: 20
  // }
});
server.applyMiddleware({ app, path });
app.listen(app.get("port"), () => {
  console.log(
    `🚀 Server ready at http://localhost:${app.get("port")}${server.graphqlPath} in ${app.get("env")} mode`
  );
  console.log("  Press CTRL-C to stop\n");
});
