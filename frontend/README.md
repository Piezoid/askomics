# Askomics frontend

This is a Node.js package for building the statics asset in `../askomics/static`.

## Usage

The assets are built by executing in this directory :
```sh
npm install
```

A development service watching source files can be started with :
```sh
npm start
```

## Webpack and TypeScript 101

### ES6 modules

With Webpack, a module is a javascript file with exports definition :
```js
export const exposedValue = 21
export function exposedFunction() {
}
// Default export
export default function MyModule() {
}
```

The exported variables are the only ones public, the other remains private and local to the module.

A module can be imported like this:
```js
// import the default export as myModule
import myModuleDefaultExport from './path/to/MyModule';
// import all the exports
import * as myModuleContent from './path/to/MyModule'
myModuleContent.exposedFunction()
// import some of the exports
import { exposedFunction } from './path/to/MyModule';
```

This is the ES6 module syntax which is rarely implemented. Modules are loaded through the typescript transpiler, to rewrites the imports and exports in the CommonJS module format (using the `require()` function). Then, the output is parsed by Webpack, in order to statically discover the dependencies between modules.

Given a entry point (like `./js/index.ts`), Webpack builds a bundle that contains all the dependencies.

#### Notes
 * `npm` packages are imported with a path like 'package-name/lib/module'. Note there is no `./` or `../` at the beginning.
 * Sometimes the `npm` packages come with two distributions, one for the browser, one for Node.js. Which one is best for Webpack depends on the module format of each distributions.

### Typescript

Typescript is a small transpiler for running static type-checking. It has two jobs :

* Type-checking
* Strip all the types annotations, and transpile ES6 syntax down to ES5.

They are independent : if the type-checking step fails, code is still emmited.

The typescript type language allows to reason on the JS object's *shape* by combining interfaces describing its properties (*i.e.* attributes in JS jargon).

```ts
interface Point {
  x:number;
  y:number;
}

function dist(p: Point): number {
  return Math.sqrt(p.x*p.x + p.y*p.y);
}

dist({x:1, y:2}) // valid
dist({x:1}) // type error, but can still be run (produce NaN)
```

It can check's that the code is correctly guarded to have the right types at the right place.
