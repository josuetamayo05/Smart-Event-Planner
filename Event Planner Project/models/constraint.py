from abc import ABC, abstractmethod

class Constraint(ABC):
    @abstractmethod
    def validate(self,resources:list, event)->bool:
        pass

class CoRequirementConstraint(Constraint):
    def __init__(self, main_resource, required_resource):
        self.main_resource = main_resource
        self.required_resource = required_resource
    def validate(self,resources:list, event)->bool:
        main_present=any(name==self.main_resource for name in resources)
        required_present=any(name==self.required_resource for name in resources)
        if main_present and not required_present:
            raise ValueError(f"❌ {self.main_resource} requiere {self.required_resource}")
        return True

class MutualExclusionConstraint(Constraint):
    def __init__(self, main_resource, exclude_resource):
        self.main_resource = main_resource
        self.exclude_resource = exclude_resource

    def validate(self,resources:list, event)->bool:
        main_present=any(name==self.main_resource for name in resources)
        main_exclude=any(name==self.exclude_resource for name in resources)
        if main_present and main_exclude:
            raise ValueError(f"{self.main_resource} no puede usarse con {self.exclude_resource}")
        return True