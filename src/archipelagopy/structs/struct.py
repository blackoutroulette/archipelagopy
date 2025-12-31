from pydantic import BaseModel, computed_field


class Struct(BaseModel):

    @computed_field(alias="class")
    def cls(self) -> str:
        return self.__class__.__name__
