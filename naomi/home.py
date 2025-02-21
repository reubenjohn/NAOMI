# Copyright 2018-2022 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import streamlit as st

from naomi.chat.chat import draw_chat
from utils import handle_login


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    if not handle_login():
        exit(0)

    draw_chat()


if __name__ == "__main__":
    run()
