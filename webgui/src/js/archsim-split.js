import Split from "split.js";

export class ArchsimSplit {
    /**
     * @param {Node} container Container of the split
     * @param {Node} firstElement First element that should be resizable
     * @param {Node} secondElement Second element that should be resizable
     */
    constructor(container, firstElement, secondElement) {
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
     * @throws {Error} Throws an error if there already is a split.
     */
    createSplit() {
        if (this.isActive) {
            throw Error("You can only create one split.");
        }
        if (window.innerWidth < window.innerHeight) {
            // Vertical split
            this.container.classList.add("vertical-split");
            this.splitInstance = Split(
                ["#" + this.firstElement.id, "#" + this.secondElement.id],
                {
                    direction: "vertical",
                    minSize: 200,
                    sizes: [60, 40],
                    snapOffset: 0,
                }
            );
        } else {
            // Horizontal split
            this.container.classList.add("horizontal-split");
            this.splitInstance = Split(
                ["#" + this.firstElement.id, "#" + this.secondElement.id],
                {
                    minSize: 200,
                    sizes: [35, 65],
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
            this.container.classList.remove(
                "horizontal-split",
                "vertical-split"
            );
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
            (this.container.classList.contains("vertical-split") &&
                window.innerWidth >= window.innerHeight) ||
            (this.container.classList.contains("horizontal-split") &&
                window.innerWidth < window.innerHeight)
        ) {
            this.destroySplit();
            this.createSplit();
        }
    }
}
