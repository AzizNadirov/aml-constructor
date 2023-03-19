from pathlib import Path
from typing import List, Union

from amlctor.utils import get_settingspy_module
from amlctor.core import PathInput, FileInput, Step, PathInputSchema, FileInputSchema, StepSchema, Pipe



class RunHandler:

    def __init__(self, path: Path):
        self.path = path
        self.check_path()
        self.settingspy = get_settingspy_module(path)


    def check_path(self):
        if self.path / 'settings' in self.path.iterdir():   # has settings dir
            settings_path = self.path / 'settings'
            files_to_check = ('.env', 'conda_dependencies.yml', 'settings.py')
            for file in files_to_check:
                if not file in settings_path.iterdir():
                    raise ValueError(
                        f"Your settings folder doesn't"
                        " '{file}' file. Make shure that you have inited pipe correctyl.")
        else:
            raise ValueError(
                'Your pipeline has no settings folder. Make shure that you have inited pipeline'
                ' and changed directory to the pipeline dir')
        


    @staticmethod
    def input_fromschema(step: StepSchema) -> List[Union[PathInput, FileInput]]:
        if not bool(step.input_data):   # there are no any input data
            return None
        
        inputs = []

        for inp in step.input_data:
            if not isinstance(inp, PathInputSchema, FileInputSchema):
                raise ValueError(f"Unknown input data: {type(inp)}")
            
            if isinstance(inp, PathInput):
                input_instance = PathInput(
                                            name=inp.name,
                                            datastore_name=inp.datastore,
                                            path_on_datasore=inp.path_on_datasore               
                    )
                inputs.append(input_instance)

            elif isinstance(inp, FileInput):
                input_instance = FileInput(
                                            name=inp.name,
                                            datastore_name=inp.datastore,
                                            path_on_datasore=inp.path_on_datasore,
                                            filename=inp.filenames,
                                            data_reference_name=inp.data_reference_name               
                    )
                inputs.append(input_instance)

            else:
                raise ValueError(f"Mysteric case: invalid input instance: '{inp}' of type: '{type(inp)}'")
        
        return inputs
    


    def step_fromschema(self, step: StepSchema) -> Step:
        step_input = RunHandler.input_fromschema(step)      # realise input data
        step_instance = Step(
            path = self.path,
            name = step.name,
            compute_target = step.compute_target,
            input_data = step_input,                        # give realised data
            allow_reuse = step.allow_reuse
        )

        return step_instance

            
    def validate(self):
        # def validate():
        #     assert isinstance(pipeline, Pipe)
        #     if not bool(pipeline.steps):
        #         raise ValueError(f"There are no steps for run...")
        pass


    def build_pipe(self) -> Pipe:
        pipe_instance = Pipe(
            name = self.settingspy['name'],
            description = self.settingspy['description'],
            steps = self.settingspy['steps'],
            continue_on_step_failure = self.settingspy['EXTRA']['continue_on_step_failure'],
            commit = False
        )

        return pipe_instance
    


    def publish(self, pipeline: Pipe):
        pipeline._publish()



    def start(self):
        self.validate()
        pipe = self.build_pipe()
        self.publish(pipeline=pipe)




