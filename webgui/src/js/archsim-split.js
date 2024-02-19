import Split from "split.js";

/**
 * Manages a split between two HTML elements that the user can resize.
 *
 * Utilises split.js.
 *
 * The split will be horizontal or vertical, depending on the device aspect ratio.
 * There is also a resize listener that changes the direction if needed.
 *
 * Because of this listener, you have to explicitly destroy objects of this class
 * (otherwise js cant garbage collect it).
 */
export class ArchsimSplit {
    /**
     * @param {Node} container Container of the split. Must already be a flex container, otherwise the split won't work.
     * @param {Node} firstElement First element that should be resizable
     * @param {Node} secondElement Second element that should be resizable
     */
    constructor(container, firstElement, secondElement) {
        /**
         * Whether the split is currently activated.
         */
        this.isActive = false;
        this.splitInstance = null;
        this.container = container;
        this.firstElement = firstElement;
        this.secondElement = secondElement;
        // bind this to handleResize so that we can use it in an event listener
        // and so we can destroy the event listener later
        this.handleResize = this.handleResize.bind(this);
        window.addEventListener("resize", this.handleResize);
    }

    /**
     * Destroys the split and also removes the resize event listener so
     * that this object no longer does anything and js can garbage collect it.
     */
    destroyObject() {
        this.destroySplit();
        removeEventListener("resize", this.handleResize);
    }

    /**
     * Creates a SplitJS split between the given elements.
     * Will be horizontal or vertical depending on the window size.
     *
     * Calling this function while the split is active won't do anything.
     */
    createSplit() {
        if (this.isActive) {
            return;
        }

        if (window.innerWidth < window.innerHeight) {
            // Vertical split
            this.container.classList.add("flex-column");
            this.splitInstance = Split(
                ["#" + this.firstElement.id, "#" + this.secondElement.id],
                {
                    direction: "vertical",
                    snapOffset: 0,
                }
            );
        } else {
            // Horizontal split
            this.splitInstance = Split(
                ["#" + this.firstElement.id, "#" + this.secondElement.id],
                {
                    snapOffset: 0,
                }
            );
        }
        this.isActive = true;
    }

    /**
     * Destroys the split. Removes the added css classes.
     * Does not do anything if the split was not constructed in the first place.
     */
    destroySplit() {
        if (this.isActive) {
            this.splitInstance.destroy();
            this.splitInstance = null;
            this.container.classList.remove("flex-column");
            this.isActive = false;
        }
    }

    /**
     * Check the viewport dimensions and switch between vertical and horizontal split if applicable.
     * Does not do anything if the split was not constructed in the first place.
     */
    handleResize() {
        if (!this.isActive) {
            return;
        }
        if (
            (this.container.classList.contains("flex-column") &&
                window.innerWidth >= window.innerHeight) ||
            (!this.container.classList.contains("flex-column") &&
                window.innerWidth < window.innerHeight)
        ) {
            this.destroySplit();
            this.createSplit();
        }
    }
}
