# Pipeline Class Documentation
This documentation will tell you, how to create your own custom pipeline using the pipeline class.
## Idea
The **pipeline** class is a framework that can be used to create your own custom pipeline implementation. It provides a basic set of methods, that are useful across different implementations. To implement your own pipeline, you will have to create  child classes of the **Stage** class and corresponding child classes of the **PipelineRegister** class.
## The pipeline class
### Arguments
> **stages**: a list of instances of child classes of the Stage class. The behavior() methods of these classes will be called during each call of step()
> **execution_ordering**: a list of indices. They provide the ordering, in which the behavior methods of the stages will be called.
> **state**:  an instance of the class ArchitecturalState on which the pipeline operates.
### Methods
> **step()**: the pipeline will do one execution cycle.
> **is_empty() -> bool**: returns true, if there are no instructions in the pipeline stages.
> **is_done()->bool**: returns true, if the pipeline is empty and there are no instructions at the current program counter.
### Functionality
The pipeline does one execution cycle whenever step() is called.
This means, that the behavior methods of the **stages** are called in the ordering provided by **execution_ordering**.
The behavior methods are called with the entire list of pipeline registers and index_of_own_input_register is set to the index of the pipeline register, that was created by the stage that is in front of the current one.
**Note**, that at any time a pipeline register in the list of pipeline registers may be just a default PipelineRegister, so the behavior methods of the stages need to be able to handle that.
This means, that the first stage does not receive a valid index (-1), since it does not have a stage the comes before it. Also the pipeline register of the last stage is not provided as direct input to any other stage.
Additionally, the pipeline will check with each step call, if a pipeline registers flush signal is set. If so, the pipeline will flush the stored pipeline registers according to the set signal.
**Note**, that if multiple flush signals are set, the one from the stage furthest back supersedes all other signals.
## The Stage class
### Methods
> **behavior(pipeline_registers, index_of_own_input_register, state)->pipeline_register**:
> This method receives all the pipeline registers and an index indicating the pipeline register of the previous stage. With this information the behavior method can modify the state and produce an output pipeline register, that will be provided to the next stage by the pipeline.
## The PipelineRegister class
### Attributes
> **instruction** the instruction, that is currently in this register. Default value is the EmptyInstruction, which just means, that there is no actual instruction in the register.
> **flush_signal** an instance of the class flush signal or None. Default value None.
### Functionality
This child classes of PipelineRegister hold the values / information of the stages. In general these should be Optionals, since some instructions may never produce some of the values .
## But how do I actually make my own pipeline
To make your own pipeline, you have to define your own child classes of the Stage class and create complementary PipelineRegister child classes. Those you will then be able to use to create your own pipeline as described above.
However be careful:
- If a stage B follows a stage A, than the pipeline register returned by stage A should be the one, that B expects to get, when it´s behaviour method accesses the pipeline register at "index_of_own_input_register".
- Also your behavior methods should be able to handle instances of the PipelineRegister super class since those are present in the pipeline after flushes, the start or end of the pipeline.
