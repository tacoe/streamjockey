# How to use classes in Sencha Touch 2

Sencha Touch 2 uses the state of the art class system developed for Ext JS 4. It makes it easy to create new classes in JavaScript, providing inheritance, dependency loading, mixins, powerful configuration options and lots more.

At its simplest, a class is just an object with some functions and properties attached to it. For instance, if we wanted to create a class for an Animal, recording its name and a function that makes it speak, we can just do this:

	Ext.define('Animal', {
		config: {
			name: null
		},
		
		speak: function() {
			alert('grunt');
		}
	});

We now have a class called Animal, where each animal can have a name and can speak. To create a new animal we just use Ext.create:

	var bob = Ext.create('Animal', {
		name: 'Bob'
	});
	
	bob.speak(); //alerts 'grunt'

Here we created an Animal called Bob and commanded it to speak. Now that we've created a class and instantiated it, we can start improving what we have. At the moment we don't know what species Bob is so let's clear that up with a Human subclass:

	Ext.define('Human', {
		extend: 'Animal',
		
		speak: function() {
			alert(this.getName());
		}
	});

Now we've got a new class that inherits from Animal, therefore gaining all of its functions and configurations. We actually overrode the speak function because most Humans are smart enough to say their name instead of grunt. Now if we make Bob a Human instead:

	var bob = Ext.create('Human', {
		name: 'Bob'
	});
	
	bob.speak(); //alerts 'Bob'

We used a magical function up above called getName. You'll notice that we didn't actually define a getName function on our Animal class, so where did it come from? Part of the class system is the ability to give classes configuration options, which each automatically give you a number of things:

* a getter function - getName() in this case - that returns the current value
* a setter function - setName() in this case - the sets a new value
* an applier function - applyName() in this case - which is called by the setter and lets you run a function when a configuration changes

The getter and setter functions are generated for free, and are the recommended way to store data in a class. Every component in Sencha Touch uses the class system and the generated function always follow the same pattern so if you know a config you already know how to get and set its value.

It also makes your own code way cleaner. For example if you wanted to always ask the user if she really wants to change Bob's name, you can just define an applyName function which will automatically be called:

	Ext.define('Human', {
		extend: 'Animal',
		
		applyName: function(newName, oldName) {
			return confirm('Are you sure you want to change name to ' + newName + '?');
		}
	});

We're just using the browser's built in confirm function which will pop open a dialog asking the user the question and offering yes and no as answers. The applier functions allow you to cancel the name change if you return false. As it happens the confirm function will return true or false depending on whether the user clicked Yes or No.

If we make a new Bob and try to change his name, but then click No when prompted, his name won't change after all:

	var bob = Ext.create('Person', {
		name: 'Bob'
	});
	
	bob.setName('Fred'); //opens a confirm box, but we click No
	
	bob.speak(); //still alerts 'Bob'

We've basically already learned the important parts of what classes are:

* All classes are defined using Ext.define, including your own classes
* Most classes extend another class, using the 'extend' syntax
* Classes are created using Ext.create - for example Ext.create('SomeClass', {some: 'configuration'})
* Always using the 'config' syntax gives you automatic getters and setters, and a much cleaner codebase

At this point you can already go about creating classes in your app, but there are a few other things the class system does.

## Dependencies and Dynamic Loading

Most of the time, classes depend on another classes. The Human class above depends on the Animal class because it extends it - we depend on Animal being present to be able to define Animal. Sometimes you'll make use of other classes inside a class, so need to guarantee that those classes are on the page. We can do this with the 'requires' syntax:

	Ext.define('Human', {
		extend: 'Animal',
		
		requires: 'Ext.MessageBox',
		
		speak: function() {
			Ext.Msg.alert()
		}
	});

When you create a class in this way, Sencha Touch will check to see if Ext.MessageBox is already loaded and if not, load it immediately. This will automatically load the required class' file over AJAX.

Ext.MessageBox itself may also have classes it depends on, which are then also loaded automatically in the background. Once all the required classes are loaded, the Human class is defined and you can start using Ext.create to instantiate people. This is great in development mode as it means you don't have to manage the loading of all your scripts yourself, but wouldn't be great in production because loading files one by one over an internet connection is rather slow.

In production, we really want to load just one JavaScript file, ideally containing only the classes that our application actually uses. This is really easy in Sencha Touch 2 due to the JSBuilder tool, which analyzes your app and creates a single file build that contains all of your classes and only the framework classes your app actually uses. See part 2 of the Getting Started guide for details on how to use the JSBuilder.

Each approach has its own pros and cons, but can we have the good parts of both at the same time while concealing the bad parts? The answer is yes, and we've implemented the solution in Sencha Touch 2.

## Naming Conventions

Using consistent naming conventions throughout your code base for classes, namespaces and filenames helps keep your code organized, structured and readable.

### 1) Classes

Class names may only contain **alphanumeric** characters. Numbers are permitted but are discouraged in most cases, unless they belong to a technical term. Do not use underscores, hyphens, or any other nonalphanumeric character. For example:

  - `MyCompany.useful_util.Debug_Toolbar` is discouraged
  - `MyCompany.util.Base64` is acceptable

Class names should be grouped into packages where appropriate and properly namespaced using object property dot-notation (.). At the minimum, there should be one unique top-level namespace followed by the class name. For example:

    MyCompany.data.CoolProxy
    MyCompany.Application

The top-level namespaces and the actual class names should be in CamelCased, everything else should be all lower-cased. For example:

    MyCompany.form.action.AutoLoad

Classes that are not distributed by Sencha should never use `Ext` as the top-level namespace.

Acronyms should also follow CamelCased convention listed above. For example:

  - `Ext.data.JsonProxy` instead of `Ext.data.JSONProxy`
  - `MyCompany.util.HtmlParser` instead of `MyCompary.parser.HTMLParser`
  - `MyCompany.server.Http` instead of `MyCompany.server.HTTP`


### 2) Source Files

The names of the classes map directly to the file paths in which they are stored. As a result, there must only be one class per file. For example:

  - `Ext.util.Observable` is stored in `path/to/src/Ext/util/Observable.js`
  - `Ext.form.action.Submit` is stored in `path/to/src/Ext/form/action/Submit.js`
  - `MyCompany.chart.axis.Numeric` is stored in `path/to/src/MyCompany/chart/axis/Numeric.js`

`path/to/src` is the directory of your application's classes. All classes should stay under this common root and should be properly namespaced for the best development, maintenance and deployment experience.

### 3) Methods and Variables

- Similarly to class names, method and variable names may only contain **alphanumeric** characters. Numbers are permitted but are discouraged in most cases, unless they belong to a technical term. Do not use underscores, hyphens, or any other nonalphanumeric character.

- Method and variable names should always be in camelCased. This also applies to acronyms.

- Examples
    - Acceptable method names:
        encodeUsingMd5()
        getHtml() instead of getHTML()
        getJsonResponse() instead of `getJSONResponse()
        parseXmlContent() instead of `parseXMLContent()
    - Acceptable variable names:
        var isGoodName
        var base64Encoder
        var xmlReader
        var httpServer

### 4) Properties

- Class property names follow the exact same convention with methods and variables mentioned above, except the case when they are static constants.

- Static class properties that are constants should be all upper-cased. For example:
    - `Ext.MessageBox.YES = "Yes"`
    - `Ext.MessageBox.NO  = "No"`
    - `MyCompany.alien.Math.PI = "4.13"`


## Hands-on

### 1. Declaration

#### 1.1) The Old Way
If you've developed with Sencha Touch 1.x, you are certainly familiar with `Ext.extend` to create a class:

    var MyPanel = Ext.extend(Object, { ... });

This approach is easy to follow to create a new class that inherits from another. Other than direct inheritance, however, we didn't have a fluent API for other aspects of class creation, such as configuration, statics and mixins. We will be reviewing these items in details shortly.

Let's take a look at another example:

    My.cool.Panel = Ext.extend(Ext.Panel, { ... });

In this example we want to [namespace][] our new class, and make it extend from `Ext.Panel`. There are two concerns we need to address:

  1. `My.cool` needs to be an existing object before we can assign `Panel` as its property
  2. `Ext.Panel` needs to exist / loaded on the page before it can be referenced

The first item is usually solved with `Ext.namespace` (aliased by `Ext.ns`). This method recursively transverse through the object / property tree and create them if they don't exist yet. The  boring part is you need to remember adding them above `Ext.extend` all the time.

    Ext.ns('My.cool');
    My.cool.Panel = Ext.extend(Ext.Panel, { ... });

The second issue, however, is not easy to address because `Ext.Panel` might depend on many other classes that it directly / indirectly inherits from, and in turn, these dependencies might depend on other classes to exist. For that reason, applications written before Sencha Touch 2 usually include the whole library in the form of `ext-all.js` even though they might only need a small portion of the framework.

### 1.2) The New Way

Sencha Touch 2 eliminates all those drawbacks with just one single method you need to remember for class creation: `Ext.define`. Its basic syntax is as follows:

    Ext.define(className, members, onClassCreated);

- `className`: The class name
- `members` is an object represents a collection of class members in key-value pairs
- `onClassCreated` is an optional function callback to be invoked when all dependencies of this class are ready, and the class itself is fully created. Due to the [new asynchronous nature](#) of class creation, this callback can be useful in many situations. These will be discussed further in [Section IV](#)

**Example:**

    Ext.define('My.sample.Person', {
        name: 'Unknown',

        constructor: function(name) {
            if (name) {
                this.name = name;
            }

            return this;
        },

        eat: function(foodType) {
            alert(this.name + " is eating: " + foodType);

            return this;
        }
    });

    var aaron = Ext.create('My.sample.Person', 'Aaron');
        aaron.eat("Salad"); // alert("Aaron is eating: Salad");

Note we created a new instance of `My.sample.Person` using the `Ext.create()` method.  We could have used the `new` keyword (`new My.sample.Person()`).  However it is recommended to get in the habit of always using `Ext.create` since it allows you to take advantage of dynamic loading.  For more info on dynamic loading see the [Getting Started guide](#/guide/getting_started)

### 2. Configuration

In Sencha Touch 2, we introduce a dedicated `config` property that gets processed by the powerful Ext.Class pre-processors before the class is created. Features include:

 - Configurations are completely encapsulated from other class members
 - Getter and setter, methods for every config property are automatically generated into the class' prototype during class creation if the class does not have these methods already defined.
 - An `apply` method is also generated for every config property.  The auto-generated setter method calls the `apply` method internally before setting the value.  Override the `apply` method for a config property if you need to run custom logic before setting the value. If `apply` does not return a value then the setter will not set the value. For an example see `applyTitle` below.

Here's an example:

    Ext.define('My.own.Window', {
       /** @readonly */
        isWindow: true,

        config: {
            title: 'Title Here',

            bottomBar: {
                enabled: true,
                height: 50,
                resizable: false
            }
        },

        constructor: function(config) {
            this.initConfig(config);

            return this;
        },

        applyTitle: function(title) {
            if (!Ext.isString(title) || title.length === 0) {
                alert('Error: Title must be a valid non-empty string');
            }
            else {
                return title;
            }
        },

        applyBottomBar: function(bottomBar) {
            if (bottomBar && bottomBar.enabled) {
                if (!this.bottomBar) {
                    return Ext.create('My.own.WindowBottomBar', bottomBar);
                }
                else {
                    this.bottomBar.setConfig(bottomBar);
                }
            }
        }
    });

And here's an example of how it can be used:

    var myWindow = Ext.create('My.own.Window', {
        title: 'Hello World',
        bottomBar: {
            height: 60
        }
    });

    alert(myWindow.getTitle()); // alerts "Hello World"

    myWindow.setTitle('Something New');

    alert(myWindow.getTitle()); // alerts "Something New"

    myWindow.setTitle(null); // alerts "Error: Title must be a valid non-empty string"

    myWindow.setBottomBar({ height: 100 }); // Bottom bar's height is changed to 100


### 3. Statics

Static members can be defined using the `statics` config

    Ext.define('Computer', {
        statics: {
            instanceCount: 0,
            factory: function(brand) {
                // 'this' in static methods refer to the class itself
                return new this({brand: brand});
            }
        },

        config: {
            brand: null
        },

        constructor: function(config) {
            this.initConfig(config);

            // the 'self' property of an instance refers to its class
            this.self.instanceCount ++;

            return this;
        }
    });

    var dellComputer = Computer.factory('Dell');
    var appleComputer = Computer.factory('Mac');

    alert(appleComputer.getBrand()); // using the auto-generated getter to get the value of a config property. Alerts "Mac"

    alert(Computer.instanceCount); // Alerts "2"


## Error Handling & Debugging

Sencha Touch 2 includes some useful features that will help you with debugging and error handling.

- You can use `Ext.getDisplayName()` to get the display name of any method.  This is especially useful for throwing errors that have the class name and method name in their description:

        throw new Error('['+ Ext.getDisplayName(arguments.callee) +'] Some message here');

- When an error is thrown in any method of any class defined using `Ext.define()`, you should see the method and class names in the call stack if you are using a WebKit based browser (Chrome or Safari).  For example, here is what it would look like in Chrome:

{@img call-stack.png}

## Further Reading

Classes are just part of the Sencha Touch 2 ecosystem. To understand more about the framework and how it works, we recommend the following:

* [Components and Containers](#!/guide/components)
* [The Data Package](#!/guide/data)
* [The Layout System](#!/guide/layouts)
* [Getting Started](#!/guide/getting_started)