// From http://xinha.python-hosting.com/wiki/NewbieGuide

xinha_editors = null;
xinha_init    = null;
xinha_config  = null;
xinha_plugins = null;

// This contains the names of textareas we will make into Xinha editors
xinha_init = xinha_init ? xinha_init : function() {
  /** STEP 1 **********************************************************
   * First, what are the plugins you will be using in the editors on
   * this page.  List all the plugins you will need, even if not all
   * the editors will use all the plugins.
   ********************************************************************/

  xinha_plugins = xinha_plugins ? xinha_plugins :
  ['CharacterMap',
   'ContextMenu',
   'FullScreen',
   'ListType',
   'SpellChecker',
   'Stylist',
   'SuperClean',
   'TableOperations'
   ];
  // THIS BIT OF JAVASCRIPT LOADS THE PLUGINS, NO TOUCHING  :)
  if(!HTMLArea.loadPlugins(xinha_plugins, xinha_init)) return;

  /** STEP 2 **********************************************************
   * Now, what are the names of the textareas you will be turning into
   * editors?
   ********************************************************************/

  xinha_editors = xinha_editors ? xinha_editors :
  ['myTextArea',
   'anotherOne'
   ];

  /** STEP 3 ***********************************************************
   * We create a default configuration to be used by all the editors.
   * If you wish to configure some of the editors differently this will be
   * done in step 5.
   *
   * If you want to modify the default config you might do something like this.
   *
   *   xinha_config = new HTMLArea.Config();
   *   xinha_config.width  = '640px';
   *   xinha_config.height = '420px';
   *
   *********************************************************************/

  xinha_config = xinha_config ? xinha_config() : new HTMLArea.Config();

  /** STEP 4 ***********************************************************
   * We first create editors for the textareas.
   *
   * You can do this in two ways, either
   *
   *   xinha_editors   = HTMLArea.makeEditors(xinha_editors, xinha_config, xinha_plugins);
   *
   * if you want all the editor objects to use the same set of plugins, OR;
   *
   *   xinha_editors = HTMLArea.makeEditors(xinha_editors, xinha_config);
   *   xinha_editors['myTextArea'].registerPlugins(['Stylist','FullScreen']);
   *   xinha_editors['anotherOne'].registerPlugins(['CSS','SuperClean']);
   *
   * if you want to use a different set of plugins for one or more of the
   * editors.
   ********************************************************************/

  xinha_editors   = HTMLArea.makeEditors(xinha_editors, xinha_config, xinha_plugins);

  /** STEP 5 ***********************************************************
   * If you want to change the configuration variables of any of the
   * editors,  this is the place to do that, for example you might want to
   * change the width and height of one of the editors, like this...
   *
   *   xinha_editors.myTextArea.config.width  = '640px';
   *   xinha_editors.myTextArea.config.height = '480px';
   *
   ********************************************************************/


  /** STEP 6 ***********************************************************
   * Finally we "start" the editors, this turns the textareas into
   * Xinha editors.
   ********************************************************************/

  HTMLArea.startEditors(xinha_editors);
}

window.onload = xinha_init;

