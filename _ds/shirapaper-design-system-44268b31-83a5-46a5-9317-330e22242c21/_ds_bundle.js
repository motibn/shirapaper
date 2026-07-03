(function () {
  function whenReact(cb) {
    if (window.React) return cb(window.React);
    var n = 0;
    (function tick() {
      if (window.React) return cb(window.React);
      if (++n > 600) return console.error('[ds] React not available');
      setTimeout(tick, 50);
    })();
  }

  function cls() {
    return Array.prototype.join.call(arguments, ' ');
  }

  whenReact(function (React) {
    var h = React.createElement;

    function Button(props) {
      var variant = props.variant || 'primary';
      var size = props.size || 'md';
      var classes = cls(
        'ds-btn',
        'ds-btn--' + variant,
        'ds-btn--' + size,
        props.pill ? 'ds-btn--pill' : '',
        props.block ? 'ds-btn--block' : ''
      );
      return h('button', {
        type: props.type || 'button',
        className: classes,
        onClick: props.onClick || props.onclick,
        children: props.children
      });
    }

    function Input(props) {
      return h('label', { className: 'ds-field' }, [
        props.label ? h('span', { className: 'ds-label', children: props.label }) : null,
        h('input', {
          className: 'ds-input',
          type: props.type || 'text',
          value: props.value || '',
          placeholder: props.placeholder || '',
          onChange: props.onChange || props.onchange
        })
      ]);
    }

    function Select(props) {
      var options = props.options || [];
      return h('label', { className: 'ds-field' }, [
        props.label ? h('span', { className: 'ds-label', children: props.label }) : null,
        h('select', {
          className: 'ds-select',
          value: props.value || '',
          onChange: props.onChange || props.onchange,
          children: options.map(function (o) {
            return h('option', { key: o.value, value: o.value, children: o.label });
          })
        })
      ]);
    }

    function Textarea(props) {
      return h('label', { className: 'ds-field' }, [
        props.label ? h('span', { className: 'ds-label', children: props.label }) : null,
        h('textarea', {
          className: 'ds-textarea',
          rows: props.rows || 3,
          value: props.value || '',
          placeholder: props.placeholder || '',
          onChange: props.onChange || props.onchange
        })
      ]);
    }

    window.ShirapaperDesignSystem_44268b = {
      Button: Button,
      Input: Input,
      Select: Select,
      Textarea: Textarea
    };
  });
})();
