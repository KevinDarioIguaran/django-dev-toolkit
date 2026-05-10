class MessageRenderer {
    static TYPES = [
        'error',
        'success',
        'warning',
        'info',
        'network'
    ];

    constructor(messageType, content = '') {
        if (!MessageRenderer.TYPES.includes(messageType)) {
            throw new Error(
                `Invalid type: '${messageType}'.`
            );
        }

        this.messageType = messageType;
        this.content = this._parse(content);
    }

    _parse(content) {
        if (typeof content === 'string') {
            return content;
        }

        if (Array.isArray(content)) {
            return content.map(item => {
                if (typeof item === 'object') {
                    return JSON.stringify(item);
                }

                return String(item);
            }).join(' ');
        }

        if (
            content &&
            typeof content === 'object'
        ) {
            return Object.values(content)
                .flatMap(v => Array.isArray(v) ? v : [v])
                .map(item => {
                    if (typeof item === 'object') {
                        return JSON.stringify(item);
                    }

                    return String(item);
                })
                .join(' ');
        }

        return String(content);
    }

    _getTarget(targetId) {
        const target = document.getElementById(targetId);

        if (!target) {
            throw new Error(
                `Element '${targetId}' not found.`
            );
        }

        return target;
    }

    _getTemplate() {
        const templateId =
            this.messageType === 'network'
                ? 'network_error'
                : `${this.messageType}_message`;

        const template = document.getElementById(templateId);

        if (!template) {
            throw new Error(
                `Template '${templateId}' not found.`
            );
        }

        return template;
    }

    render(targetId) {
        const target = this._getTarget(targetId);
        const template = this._getTemplate();

        const clone = template.content.cloneNode(true);

        if (this.messageType !== 'network') {
            const textEl =
                clone.querySelector('[data-message-text]') ||
                clone.querySelector('[id$="_message_text"]');

            if (textEl) {
                textEl.textContent = this.content;
            }
        }

        target.replaceChildren(clone);
    }

    hide(targetId) {
        const target = this._getTarget(targetId);

        target.replaceChildren();
    }

    toggle(targetId) {
        const target = this._getTarget(targetId);

        if (target.children.length > 0) {
            this.hide(targetId);
            return;
        }

        this.render(targetId);
    }
}